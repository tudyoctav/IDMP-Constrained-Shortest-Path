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


OUTPUT_FOLDER = Path("output/")
TIME_WINDOW_FILE = OUTPUT_FOLDER / "sat_tw_csp.csv"
RESOURCE_CONSTRAINED_FILE = OUTPUT_FOLDER / "sat_rc_csp.csv"
MODEL = Path(__file__).parent / "model"
TW_KEY = "time_window"
RC_KEY = "resource_constraint"
FIRST_ROW = ["name", "exit status", "time spend", "optimal value"]

def init_arg_parse():
    parser = argparse.ArgumentParser(
        description='Solver for time_window and resource_constrained Shortest Path problems ')
    parser.add_argument("-t", "--time-out", nargs=1, dest="time_out", type=int, default=60)
    parser.add_argument("-o", "--output_file", nargs=1, dest="output_file", type=Path, default=None)
    parser.add_argument("problem_type", help="The problem type to solve.", choices=[
                        "resource_constraint", "time_window"])
    parser.add_argument("instance_folder", type=Path,
                        help="The folder containing instance files to run.")
    return vars(parser.parse_args())


def get_command(problem_type: str, file: Path):
    match problem_type:
        case "resource_constraint":
            return [sys.executable, MODEL, RC_KEY, file]
        case "time_window":
            return [sys.executable, MODEL, TW_KEY, file]
        case _:
            raise BaseException(f"problem type not found: '{problem_type}'")

class ExitStatus(Enum):
    succes   ="*** Succes ***"
    time_out ="*** Timeout ***"
    interrupt="*** Interrupt ***"

def run_file(problem_type: str, file: Path, time_out: int, **_vargs):
    command = get_command(problem_type, file)
    output = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
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
def parse_output(exit_status: ExitStatus, output: str):
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
    if output_file != None:
        return output_file
    match problem_type:
        case "resource_constraint":
            return RESOURCE_CONSTRAINED_FILE
        case "time_window":
            return TIME_WINDOW_FILE
        case _:
            raise BaseException(f"problem type not found: '{problem_type}'")

def make_output_file(**vargs) -> Path:
    out_file = get_output_file(**vargs)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    if not out_file.exists():
        with open(out_file, "w") as writable_out_file:
            csv_writer = csv.writer(writable_out_file)
            csv_writer.writerow(["name", "exit status", "time spend", "optimal value"])
    return out_file



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
            status, res = run_file(problem_type, file, **vargs)
            time, optim_val = parse_output(status, res)
            csv_writer.writerow([file.name, status.value, time, optim_val])
        

if __name__ == "__main__":
    main(**init_arg_parse())
