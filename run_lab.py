#! /usr/bin/env python

from pathlib import Path
import platform
import os

import pandas as pd
from lab_report import FunctionReport
import run_lab_helper
from downward.reports.absolute import AbsoluteReport, PlanningReport
from lab.environments import BaselSlurmEnvironment, LocalEnvironment
from lab.experiment import Experiment
from lab.reports import Attribute, arithmetic_mean
import matplotlib.pyplot as plt

# Create custom report class with suitable info and error attributes.


class BaseReport(AbsoluteReport):
    INFO_ATTRIBUTES = ["problem", "time_limit", "memory_limit",
                       "path_length", "solve_time", "run_index", "solver_exit_code", "command"]
    ERROR_ATTRIBUTES = [
        "domain",
        "algorithm",
        "problem",
        "unexplained_errors",
        "error",
        "node",
        "solver_exit_code"
    ]


NODE = platform.node()
REMOTE = NODE.endswith(
    ".scicore.unibas.ch") or NODE.endswith(".cluster.bc2.ch")
SCRIPT_DIR = Path(__file__).parent
BENCHMARKS_DIR = SCRIPT_DIR / Path("cp/minizinc/Variants/data/")
FRCSP_INSTANCES = sorted((BENCHMARKS_DIR / "frcsp").glob("**/*.dzn"))
TCSP_INSTANCES = sorted((BENCHMARKS_DIR / "tcsp").glob("**/*.dzn"))
NCSP_INSTANCES = sorted((BENCHMARKS_DIR / "ncsp").glob("**/*.dzn"))
SEED = 42
MEMORY_LIMIT = None  # MiB
EMAIL = os.environ.get('email', None)
SUITE = FRCSP_INSTANCES

if REMOTE:
    ENV = BaselSlurmEnvironment(email=os.environ['email'])
    TIME_LIMIT = 60  # seconds
else:
    ENV = LocalEnvironment(processes=5)
    # Use lower timeout for local tests.
    TIME_LIMIT = 1  # seconds
SUMMARY_ATTRIBUTES = [
    Attribute("path_length", function=max),
    Attribute("solve_time", function=arithmetic_mean, digits=5),
    Attribute("solver_exit_code", function=run_lab_helper.count_non_zero),
    Attribute("solved", absolute=True),
]
ATTRIBUTES = ["domain", "algorithm", "solver", "run_index", "node", "solver_exit_code",
              "solved", "path_length", Attribute("solve_time", function=arithmetic_mean, digits=5)]


# Create a new experiment.
exp = Experiment(environment=ENV)
# # Add solver to experiment and make it available to all runs.
# exp.add_resource("solver", os.path.join(SCRIPT_DIR, "solver.py"))
# Add custom parser.
exp.add_parser("parser_lab.py")

runs = []
for problem in FRCSP_INSTANCES:
    runs.extend(run_lab_helper.make_runs(
        exp, problem, "time_window", TIME_LIMIT, MEMORY_LIMIT))
for problem in FRCSP_INSTANCES:
    runs.extend(run_lab_helper.make_runs(
        exp, problem, "resource_constrained", TIME_LIMIT, MEMORY_LIMIT))
for problem in NCSP_INSTANCES:
    runs.extend(run_lab_helper.make_runs(
        exp, problem, "node", TIME_LIMIT, MEMORY_LIMIT))
for problem in TCSP_INSTANCES:
    runs.extend(run_lab_helper.make_runs(
        exp, problem, "unordered_task", TIME_LIMIT, MEMORY_LIMIT))

# Add step that writes experiment files to disk.
exp.add_step("build", exp.build)

# Add step that executes all runs.
exp.add_step("start", exp.start_runs)

exp.add_parse_again_step()

# Add step that collects properties from run directories and
# writes them to *-eval/properties.
exp.add_fetcher(name="fetch")


def problem_type(problem_type: str):
    def filter(run):
        return run["problem_type"] == problem_type
    return filter


def timeout(run: dict):
    return run.get("solve_time", None) != None


# Make a report.
exp.add_report(PlanningReport())
exp.add_report(BaseReport(attributes=SUMMARY_ATTRIBUTES, filter=[timeout, problem_type(
    "time_window")], format="html"), outfile="report_time_window.html")
exp.add_report(BaseReport(attributes=SUMMARY_ATTRIBUTES, filter=[timeout, problem_type(
    "resource_constrained")], format="html"), outfile="report_time_constraint.html")
exp.add_report(BaseReport(attributes=SUMMARY_ATTRIBUTES, filter=[problem_type(
    "unordered_task")], format="html"), outfile="report_unordered_task.html")
exp.add_report(BaseReport(attributes=SUMMARY_ATTRIBUTES, filter=[
               timeout, problem_type("node")], format="html"), outfile="report_node.html")


def plot_times(data: pd.DataFrame, out_file):
    maximum = data["time_limit"].max()
    data = data[["algorithm", "solver", "domain", "solve_time"]] \
        .groupby(["algorithm", "solver", "domain"])\
        .mean()
    fig = plt.figure(figsize=(10, 5))
    for (alg, solver), frame in data.groupby(["algorithm", "solver"]):
        frame = sorted(frame.loc[frame["solve_time"].notnull(), "solve_time"])
        plt.stairs(frame + [maximum], list(range(len(frame) + 1)) + [len(frame)],
                   baseline=None, orientation="horizontal", label=f"{alg}")
    plt.xlabel("Time (s)")
    plt.ylabel("Number of solved problems")
    plt.legend()
    plt.savefig(out_file)


exp.add_report(FunctionReport(plot_times, ATTRIBUTES, filter_problem_type="resource_constrained", filter_algorithm=[
               "RCSP", "RCSP-bool_search(x,dom_w_deg, indomain_min)-restart_linear(1000).mzn", "sat(solver:cadical153)", "sat(solver:m22)"]), name="plot_times_resource_constrained", outfile="resource_constrained_plot.png")

# Parse the commandline and run the given steps.
exp.run_steps()
