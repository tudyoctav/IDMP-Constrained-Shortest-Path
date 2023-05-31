from pathlib import Path
from lab.experiment import Experiment, Run
from typing import List
import sys

NUM_OF_RUNS = 3
PYTHON = sys.executable


def make_runs(exp: Experiment, problem: Path, problem_type: str, time_limit: str, memory_limit: str) -> List[Run]:
    res: List[Run] = []
    for i in range(NUM_OF_RUNS):
        res.extend(make_cp_runs(exp, problem, problem_type,
                   time_limit, memory_limit, i))
        res.extend(make_sat_runs(exp, problem, problem_type,
                   time_limit, memory_limit, i))
        res.extend(make_mip_runs(exp, problem, problem_type,
                   time_limit, memory_limit, i))
    for run in res:
        run.add_resource("problem", problem, symlink=True)
        run.set_property("problem", problem.name)
        run.set_property("domain", problem_type)
        run.set_property("time_limit", time_limit)
        run.set_property("memory_limit", memory_limit)
    return res


def make_cp_runs(exp: Experiment, problem: Path, problem_type: str, time_limit: str, memory_limit: str, run_i: int) -> List[Run]:
    res = []
    BASE_ID = ["cp", problem_type, str(problem)]

    for solver in ["Gecode"]:
        if problem.suffix != ".dzn":
            print("problem {problem} is not a supported format for cp!")
            continue
        match problem_type:
            case "time_window":
                for model in Path("cp/minizinc/Variants").glob("FRCSP*.mzn"):
                    run = exp.add_run()
                    

                    run.add_resource("model", model.absolute(), symlink=True)
                    run.add_command("solve", ["minizinc", "--output-time", "-s", "--solver", solver, "{model}", "{problem}"], time_limit, memory_limit)

                    run.set_property("solver", solver)
                    run.set_property("id", BASE_ID + [solver, f"run_{run_i}"])
                    run.set_property("algorithm", model.name)

                    res.append(run)
            case "resource_constrained":
                pass
            case "node":
                pass
            case "ordered_task":
                pass
            case "unordered_task":
                pass
            case _:
                raise NotImplementedError()
    return res


def make_sat_runs(exp: Experiment, problem: Path, problem_type: str, time_limit: str, memory_limit: str, run_i: int) -> List[Run]:
    res = []
    BASE_ID = ["sat", problem_type, str(problem)]
    for solver in ["m22", "cadical153"]:
        run = exp.add_run()
        res.append(run)
        run.set_property("solver", solver)
        # Every run should have a unique id
        run.set_property("id", BASE_ID + [solver, f"run_{run_i}"])
        run.set_property("algorithm", "sat")

        match problem_type:
            case "time_window" | "resource_constrained":
                # resources that are needed for running should be added
                run.add_resource("model", Path(
                    "sat/model").absolute(), symlink=True)
                run.add_command("solve", [PYTHON, "{model}", "--solver", solver,
                                problem_type, "{problem}"], time_limit, memory_limit)
            case "node" | "ordered_task" | "unordered_task":
                run = exp.add_run()
                problem_val = "{problem}"
                if problem.suffix == ".dzn":
                    # TODO Doesn't work yet converter needs updating
                    continue
                    run.add_resource("converter", Path("sat-node-task/convert.py").absolute(), symlink=True)
                    problem_val = "temp_file.txt"
                    run.add_command("convert_dzn2txt", [PYTHON, "{converter}", problem_val])
                run.add_resource("model", Path(
                    "sat-node-task/sat_directed_edges-idpool.py").absolute(), symlink=True)
                run.add_command(
                    "solve", [PYTHON, "{model}", problem_val, problem_type, solver], time_limit, memory_limit)
            case _:
                raise NotImplementedError(f"{problem_type} is not implemented for sat")
            
    return res


def make_mip_runs(exp: Experiment, problem: Path, problem_type: str, time_limit: str, memory_limit: str, run_i: int) -> List[Run]:
    res = []
    match problem_type:
        case "time_window":
            pass
        case "resource_constrained":
            pass
        case "node":
            pass
        case "ordered_task":
            pass
        case "unordered_task":
            pass
        case _:
            raise NotImplementedError()
    return res
