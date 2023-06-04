#!/usr/bin/env python
from enum import Enum
from pathlib import Path
import subprocess
import sys
import argparse
import re
import csv
import sys
from time import sleep
from tqdm import tqdm
import numpy as np
from typing import List

# Defaults
OUTPUT_FOLDER = Path("output/")
TIME_WINDOW_FILE = OUTPUT_FOLDER / "sat_tw_csp.csv"
RESOURCE_CONSTRAINED_FILE = OUTPUT_FOLDER / "sat_rc_csp.csv"
MODEL = Path(__file__).parent / "model"
TW_KEY = "time_window"
RC_KEY = "resource_constraint"
TIME_OUT = 60
SOLVERS = ["cadical153"]
REPEATS = 3


class ExitStatus(Enum):
    succes = "*** Succes ***"
    time_out = "*** Timeout ***"
    interrupt = "*** Interrupt ***"


def init_arg_parse(args=None):
    """Initializes the argparser for parsing command line arguments."""
    parser = argparse.ArgumentParser(
        description='Solver runner for time_window and resource_constrained Shortest Path problems ')
    parser.add_argument("-t", "--time-out", dest="time_out",
                        type=int, help="The timeout after which to terminate the solver in seconds", default=TIME_OUT)
    parser.add_argument("-o", "--output_file", dest="output_file", type=Path,
                        help="The file to write the timing information to.", default=None)
    parser.add_argument("-s", "--solvers", dest="solvers", nargs="+",
                        help="The name of the solvers to use, more than one value can be specified.", default=SOLVERS)
    parser.add_argument("-r", "--repeats", type=int,
                        help="The number of times to repeat the solver to get an average", default=REPEATS)
    parser.add_argument("--std_out_dir", dest="std_out_dir", type=Path,
                        help="Path to folder where to store the outputs of the solvers.", default=Path("output_sat"))

    parser.add_argument(
        "problem_type", help="The problem type to solve.", choices=[RC_KEY, TW_KEY])
    parser.add_argument("instance_folder", type=Path,
                        help="The folder containing instance files to run.")
    return vars(parser.parse_args(args))


def get_command(problem_type: str, file: Path, solver: str) -> List[str]:
    """Retrieves the command to start the solver."""
    match problem_type:
        case "resource_constraint":
            return [sys.executable, MODEL, RC_KEY, file, "-s", solver]
        case "time_window":
            return [sys.executable, MODEL, TW_KEY, file, "-s", solver]
        case _:
            raise BaseException(f"problem type not found: '{problem_type}'")


def run_file(problem_type: str, file: Path, solver: str, time_out: int, **_vargs) -> tuple[ExitStatus, str]:
    """Runs the specified file with the current problem type and returns it exit status and its output"""
    command = get_command(problem_type, file, solver)
    output = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    try:
        output.wait(time_out)
        return ExitStatus.succes, output.stdout.read()
    except subprocess.TimeoutExpired:
        output.kill()
        return ExitStatus.time_out, output.stdout.read()
    except KeyboardInterrupt:
        sleep(2)
        print("Got KeyBoardIntrerup")
        output.kill()
        return ExitStatus.interrupt, output.stdout.read()


TIME_REGEX = re.compile(r"% time elapsed: (?P<val>.*)")
OPTIM_VAL_REGEX = re.compile(r"optimal val is: (?P<val>.*)")


def parse_output(exit_status: ExitStatus, output: str) -> tuple[float, int]:
    """Parses the output generated by a solver and returns the runtime in seconds and the optimal value found"""
    match exit_status:
        case ExitStatus.succes:
            time = TIME_REGEX.search(output)
            time = float(time.group("val")) if time else None
            optim_val = OPTIM_VAL_REGEX.search(output)
            optim_val = int(optim_val.group("val")) if optim_val else None
            return time, optim_val
        case _:
            return None, None


def get_output_file(problem_type: str, output_file: Path, **_vargs) -> Path:
    """Retrieves the output files from the options or uses the default for this problem type."""
    if output_file != None:
        return output_file
    match problem_type:
        case "resource_constraint":
            return RESOURCE_CONSTRAINED_FILE
        case "time_window":
            return TIME_WINDOW_FILE
        case _:
            raise BaseException(f"problem type not found: '{problem_type}'")


def make_output_file(solvers: List[str], **vargs) -> Path:
    """Construct the output CSV and setups the first row returns the Path to this file."""
    out_file = get_output_file(**vargs)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w") as writable_out_file:
        csv_writer = csv.writer(writable_out_file)
        csv_writer.writerow(
            ["instance", *solvers])
    return out_file


def save_std_out(std_out: str, run: int, solver: str, file: Path, problem_type: str, std_out_dir: Path, **vargs):
    """Saves the output of a solver to file for ease of debugging later."""
    solver_out_dir = std_out_dir / problem_type / solver
    solver_out_dir.mkdir(parents=True, exist_ok=True)
    outfile = solver_out_dir / f"{file.stem}_run{run}.txt"
    with open(outfile, "w") as outfile:
        outfile.write(std_out)


def repeat_run(problem_type: str, file: Path, repeats: int, solvers: List[str], **vargs):
    """Runs `file` `repeats` number of times with all `solvers` and returns average times
    
    Returns
    ----------
        A list of length `len(solvers)` containing the avaraged results.
    """
    avg_times = []
    for solver in solvers:
        times = []
        for i in range(repeats):
            status, res = run_file(problem_type, file, solver, **vargs)
            save_std_out(res, i, solver, file, problem_type, **vargs)
            if status != ExitStatus.succes:
                times.append("t/o")
                break
            time, optim_val = parse_output(status, res)
            times.append(time)
        if times[-1] == "t/o":
            avg_times.append("t/o")
        else:
            avg_times.append(np.mean(times))
    return avg_times


DATA_FILE_RE = re.compile(r".*(.dzn)|(.txt)")

def main(problem_type: str, instance_folder: Path, **vargs):
    print(problem_type, instance_folder)
    assert instance_folder.is_dir(), "Provided folder should be a directory"
    with open(make_output_file(problem_type=problem_type, **vargs), "a") as out_file:
        csv_writer = csv.writer(out_file)
        for file in tqdm(list(instance_folder.iterdir())):
            if not DATA_FILE_RE.fullmatch(file.name):
                print("skipping file with unkown format:", file)
                continue
            avg_times = repeat_run(problem_type, file, **vargs)
            csv_writer.writerow(
                [file.relative_to(instance_folder), *avg_times])

def run_all(problem_type: str, instance_folder: Path, **vargs):
    """Runs all tests specified in the instance_folder
    Works teh same as the command line version but is easier to call from inside python.

    Examples
    ----------
    >>> run_all("resource_constraint", "cp/minizinc/Variants")
    Set timeout from default to 5 seconds
    >>> run_all("resource_constraint", "cp/minizinc/Variants", timeout=5)
    
    Parameters
    ----------
        problem_type : one of >>> ["time_window", "resource_constraint"].
        instance_folder : The Path to the folder containing all test instances to run.
        For more parameters run `python run_all.py -h`
    """
    new_vargs = init_arg_parse([problem_type, instance_folder])
    for key in vargs:
        assert key in new_vargs.keys(), f"Unkown option `{key}` allowed options: {new_vargs.keys()}"
    new_vargs.update(vargs)
    main(**new_vargs)

if __name__ == "__main__":
    main(**init_arg_parse())