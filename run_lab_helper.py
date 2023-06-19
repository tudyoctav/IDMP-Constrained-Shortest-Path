from copy import copy
from functools import cache
from pathlib import Path
from lab.experiment import Experiment, Run
from typing import List
import sys

NUM_OF_RUNS = 3
PYTHON = sys.executable


def make_runs(exp: Experiment, problem: Path, problem_type: str, time_limit: str, memory_limit: str, run_i: int) -> List[Run]:
    res: List[Run] = []
    res.extend(make_cp_runs(exp, problem, problem_type,
                time_limit, memory_limit, run_i))
    res.extend(make_sat_runs(exp, problem, problem_type,
                time_limit, memory_limit, run_i))
    res.extend(make_mip_runs(exp, problem, problem_type,
                time_limit, memory_limit, run_i))
    for run in res:
        run.add_resource("problem", problem, symlink=False)
        run.set_property("problem", problem.stem)
        run.set_property("problem_type", problem_type)
        run.set_property("domain", problem.stem)
        run.set_property("time_limit", time_limit)
        run.set_property("memory_limit", memory_limit)
    return res


def make_cp_runs(exp: Experiment, problem: Path, problem_type: str, time_limit: str, memory_limit: str, run_i: int) -> List[Run]:
    if problem.suffix != ".dzn":
        return []
    res = []
    BASE_ID = ["cp", problem_type, str(problem)]

    for solver in ["Gecode"]:
        if problem.suffix != ".dzn":
            print(f"problem {problem} is not a supported format for cp!")
            continue
        match problem_type:
            case "time_window":
                for model in Path("cp/minizinc/Variants").glob("FRCSP*.mzn"):
                    run = exp.add_run()
                    

                    run.add_resource("model", model.absolute())
                    run.add_command("solve", ["minizinc", "--output-time", "-s", "--solver", solver, "{model}", "{problem}"], time_limit, memory_limit)

                    run.set_property("solver", solver)
                    run.set_property("id", BASE_ID + [model.stem, solver, f"run_{run_i}"])
                    run.set_property("algorithm", model.stem)

                    res.append(run)
            case "resource_constrained":
                for model in Path("cp/minizinc/Variants").glob("RCSP*.mzn"):
                    run = exp.add_run()
                    
                    run.add_resource("model", model.absolute())
                    run.add_command("solve", ["minizinc", "--output-time", "-s", "--solver", solver, "{model}", "{problem}"], time_limit, memory_limit)

                    run.set_property("solver", solver)
                    run.set_property("id", BASE_ID + [model.stem, solver, f"run_{run_i}"])
                    run.set_property("algorithm", model.stem)

                    res.append(run)
            case "node":
                for model in Path("cp/minizinc/Variants").glob("NCSP*.mzn"):
                    run = exp.add_run()
                    
                    run.add_resource("model", model.absolute())
                    run.add_command("solve", ["minizinc", "--output-time", "-s", "--solver", solver, "{model}", "{problem}"], time_limit, memory_limit)

                    run.set_property("solver", solver)
                    run.set_property("id", BASE_ID + [model.stem, solver, f"run_{run_i}"])
                    run.set_property("algorithm", model.stem)

                    res.append(run)
                pass
            case "ordered_task":
                pass
            case "unordered_task":
                for model in Path("cp/minizinc/Variants").glob("TCSP*.mzn"):
                    run = exp.add_run()
                    
                    run.add_resource("model", model.absolute())
                    run.add_command("solve", ["minizinc", "--output-time", "-s", "--solver", solver, "{model}", "{problem}"], time_limit, memory_limit)

                    run.set_property("solver", solver)
                    run.set_property("id", BASE_ID + [model.stem, solver, f"run_{run_i}"])
                    run.set_property("algorithm", model.stem)

                    res.append(run)
                pass
            case _:
                raise NotImplementedError()
    for run in res:
        run.set_property("run_index", str(run_i))
    return res


def make_sat_runs(exp: Experiment, problem: Path, problem_type: str, time_limit: str, memory_limit: int, run_i: int) -> List[Run]:
    res = []
    BASE_ID = ["sat", problem_type, str(problem)]
    for solver in ["cadical153"]:

        run = exp.add_run()
        res.append(run)
        run.set_property("solver", solver)
        # Every run should have a unique id
        run.set_property("id", BASE_ID + [solver, f"run_{run_i}"])
        run.set_property("algorithm", "sat")

        match problem_type:
            case "time_window" | "resource_constrained":
                # resources that are needed for running should be added
                if problem.suffix != ".dzn":
                    # Remove run and exit not correct format!
                    exp.runs.pop()
                    return []
                run.add_resource("model", Path(
                    "sat/model").absolute(), symlink=True)
                run.add_command("solve", [PYTHON, "{model}", "--solver", solver,
                                problem_type, "{problem}"], time_limit, memory_limit)
            case "node" | "ordered_task" | "unordered_task":
                problem_val = "{problem}"
                if problem.suffix != ".txt":
                    # Remove run and exit not correct format!
                    exp.runs.pop()
                    return []
                run.add_resource("model", Path(
                    "sat-node-task/sat_directed_edges-idpool.py").absolute(), symlink=True)
                run.add_command(
                    "solve", [PYTHON, "{model}", problem_val, problem_type, solver], time_limit, memory_limit)
            case _:
                raise NotImplementedError(f"{problem_type} is not implemented for sat")
    for run in res:
        run.set_property("run_index", str(run_i))
    return res

MIP_SOVLER = Path("RCSP-MIP/build/RCSP-MIP")
@cache
def get_mip_solver():
    mip_solver = copy(MIP_SOVLER)
    if mip_solver.exists():
        return mip_solver
    mip_solver.suffix=".exe"
    if mip_solver.exists():
        return mip_solver
    print(f"Warning could not find: {mip_solver} please make sure that you have a compiled mip solver inside the RCSP-MIP/build!")
    return None

def make_mip_runs(exp: Experiment, problem: Path, problem_type: str, time_limit: str, memory_limit: str, run_i: int) -> List[Run]:
    if problem.suffix != ".inst":
        return []
    res = []
    model = get_mip_solver()
    run = exp.add_run()
    res.append(run)
    run.set_property("solver", "cplex")
    # Every run should have a unique id
    run.set_property("id", ["cp", problem_type, str(problem), "cplex", f"run_{run_i}"])
    run.set_property("algorithm", "mip")
    run.add_resource("model", model.absolute(), symlink=True)
    match problem_type:
        case "resource_constrained":
            run.add_command("solve", ["./{model}", "ifile", "{problem}", "prob", "RCSP"], time_limit, memory_limit)
        case "node":
            run.add_command("solve", ["./{model}", "ifile", "{problem}", "prob", "NCSP"], time_limit, memory_limit)
        case "unordered_task":
            run.add_command("solve", ["./{model}", "ifile", "{problem}", "prob", "TCSP"], time_limit, memory_limit)
        case _:
            exp.runs.pop()
            res.pop()
    return res

def count_non_zero(values: list):
    res = 0
    for value in values:
        if value != 0:
            res += 1
    return res