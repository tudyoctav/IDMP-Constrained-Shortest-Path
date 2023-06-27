#! /usr/bin/env python

from pathlib import Path
import platform
import os

import pandas as pd
from lab_report import CSVReport, FunctionReport
import run_lab_helper
from downward.reports.absolute import AbsoluteReport, PlanningReport
from lab.environments import BaselSlurmEnvironment, LocalEnvironment
from lab.experiment import Experiment
from lab.reports import Attribute, arithmetic_mean
import matplotlib.pyplot as plt

from table_gen import rcsp_report, tcsp_report, ncsp_report

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
BENCHMARKS_DIR = SCRIPT_DIR / Path("graph_generation/data")
FRCSP_INSTANCES = sorted(BENCHMARKS_DIR.glob("**/rcsp/*"))
TWCSP_INSTANCES = sorted(BENCHMARKS_DIR.glob("**/rcsp/*"))
TCSP_INSTANCES = sorted(BENCHMARKS_DIR.glob("**/tcsp/*"))
NCSP_INSTANCES = sorted(BENCHMARKS_DIR.glob("**/ncsp/*"))
SEED = 42
MEMORY_LIMIT = 4000  # MiB
EMAIL = os.environ.get('email', None)
NUM_RUNS = 3

if REMOTE:
    ENV = BaselSlurmEnvironment(email=EMAIL)
    TIME_LIMIT = 60  # seconds
else:
    ENV = LocalEnvironment(processes=None)
    # Use lower timeout for local tests.
    TIME_LIMIT = 60  # seconds
SUMMARY_ATTRIBUTES = [
    Attribute("path_length", function=max),
    Attribute("solve_time", function=arithmetic_mean, digits=5),
    Attribute("solver_exit_code", function=run_lab_helper.count_non_zero),
    Attribute("solved", absolute=True),
]
ATTRIBUTES = ["problem", "problem_type", "algorithm", "solver", "run_index", "node", "solver_exit_code",
              "solved", "path_length", Attribute("solve_time", function=arithmetic_mean, digits=5), "run_dir"]


# Create a new experiment.
exp = Experiment(environment=ENV)
# # Add solver to experiment and make it available to all runs.
# exp.add_resource("solver", os.path.join(SCRIPT_DIR, "solver.py"))
# Add custom parser.
exp.add_parser("parser_lab.py")

runs = []
for i in range(NUM_RUNS):
    for problem in FRCSP_INSTANCES:
        runs.extend(run_lab_helper.make_runs(
            exp, problem, "time_window", TIME_LIMIT, MEMORY_LIMIT, i))
    for problem in TWCSP_INSTANCES:
        temp = run_lab_helper.make_runs(
            exp, problem, "resource_constrained", TIME_LIMIT, MEMORY_LIMIT, i)
        # Fix mip being in wrong catagory
        for run in temp:
            if run.properties["technology"] == "mip":
                run.set_property("problem_type", "time_window")    
        runs.extend(temp)
    for problem in NCSP_INSTANCES:
        runs.extend(run_lab_helper.make_runs(
            exp, problem, "node", TIME_LIMIT, MEMORY_LIMIT, i))
    for problem in TCSP_INSTANCES:
        runs.extend(run_lab_helper.make_runs(
            exp, problem, "unordered_task", TIME_LIMIT, MEMORY_LIMIT, i))

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
    return run.get("solved", None) == 1


# Make a report.
exp.add_report(PlanningReport(attributes=ATTRIBUTES))

exp.add_report(CSVReport(attributes=ATTRIBUTES), outfile="all_results.csv")
exp.add_report(CSVReport(attributes=ATTRIBUTES,
               filter_problem_type="time_window"), outfile="time_window_results.csv")
exp.add_report(CSVReport(attributes=ATTRIBUTES,
               filter_problem_type="resource_constrained"), outfile="resource_results.csv")
exp.add_report(CSVReport(attributes=ATTRIBUTES,
               filter_problem_type="unordered_task"), outfile="unordered_task_results.csv")
exp.add_report(CSVReport(attributes=ATTRIBUTES,
               filter_problem_type="node"), outfile="node_results.csv")

# exp.add_report(BaseReport(attributes=SUMMARY_ATTRIBUTES, filter=[timeout, problem_type(
#     "time_window")], format="html"), outfile="report_time_window.html")
# exp.add_report(BaseReport(attributes=SUMMARY_ATTRIBUTES, filter=[timeout, problem_type(
#     "resource_constrained")], format="html"), outfile="report_time_constraint.html")
# exp.add_report(BaseReport(attributes=SUMMARY_ATTRIBUTES, filter=[timeout, problem_type(
#     "unordered_task")], format="html"), outfile="report_unordered_task.html")
# exp.add_report(BaseReport(attributes=SUMMARY_ATTRIBUTES, filter=[
#                timeout, problem_type("node")], format="html"), outfile="report_node.html")


def plot_times(data: pd.DataFrame, out_file):
    maximum = data["time_limit"].max()
    data = data[["algorithm", "solver", "domain", "solve_time"]] \
        .groupby(["algorithm", "solver", "domain"])\
        .mean()
    fig = plt.figure(figsize=(10, 5))
    # plt.title("Number of solved resource constrained instances over time spend solving")
    for (alg, solver), frame in data.groupby(["algorithm", "solver"]):
        frame = sorted(frame.loc[frame["solve_time"].notnull(), "solve_time"])
        frame = list(filter(lambda x: x < maximum, frame))
        plt.stairs(frame + [maximum], list(range(len(frame) + 1)) + [len(frame)],
                   baseline=None, orientation="horizontal", label=f"{alg}")
    plt.xlabel("Time (s)")
    plt.ylabel("Number of solved problems")
    # plt.yticks(range(7))
    plt.ylim(bottom=0)
    plt.legend()
    plt.savefig(out_file)


# exp.add_report(FunctionReport(plot_times, ATTRIBUTES, filter_problem_type="time_window", filter_algorithm=[
#                "","sat"]), name="plot_time_window", outfile="tw_plot.png")
exp.add_report(FunctionReport(plot_times, ATTRIBUTES, filter_problem_type="resource_constrained", filter_algorithm=[
               "RCSP", "RCSP-dpath-bool_search(x,dom_w_deg, indomain_min)-restart_linear(1000)", "sat", "mip"]), name="plot_resource", outfile="resource_plot.png")
exp.add_report(FunctionReport(plot_times, ATTRIBUTES, filter_problem_type="time_window", filter_algorithm=[
               "FRCSP", "FRCSP-dpath-bool_search(x,dom_w_deg, indomain_min)-restart_linear(1000)", "sat", "mip"]), name="plot_time_window", outfile="time_window_plot.png")
exp.add_report(FunctionReport(plot_times, ATTRIBUTES, filter_problem_type="unordered_task", filter_algorithm=[
               "TCSP", "TCSP_bounded_search_restart", "sat", "mip"]), name="plot_task", outfile="unordered_task_plot.png")
exp.add_report(FunctionReport(plot_times, ATTRIBUTES, filter_problem_type="node", filter_algorithm=[
               "NCSP", "NCSP_bounded_search_restart", "sat", "mip"]), name="plot_node", outfile="node_plot.png")

exp.add_report(FunctionReport(rcsp_report, ATTRIBUTES, filter_problem_type="resource_constrained", filter_technology="cp"), name="cp_rcsp_table", outfile="cp_rcsp_table.tex")
exp.add_report(FunctionReport(rcsp_report, ATTRIBUTES, filter_problem_type="resource_constrained", filter_technology="sat"), name="sat_rcsp_table", outfile="sat_rcsp_table.tex")
for technology in ["cp", "sat", "mip"]:
    exp.add_report(FunctionReport(rcsp_report, ATTRIBUTES, filter_problem_type="time_window", filter_technology=technology), name=f"{technology}_tw_table",outfile=f"{technology}_twsp_table.tex")
    exp.add_report(FunctionReport(tcsp_report, ATTRIBUTES, filter_problem_type="unordered_task", filter_technology=technology), name=f"{technology}_tcsp_table",outfile=f"{technology}_tcsp_table.tex")
    exp.add_report(FunctionReport(ncsp_report, ATTRIBUTES, filter_problem_type="node", filter_technology=technology), name=f"{technology}_ncsp_table",outfile=f"{technology}_ncsp_table.tex")
# Parse the commandline and run the given steps.
exp.run_steps()
