#! /usr/bin/env python

from pathlib import Path
import platform
import os
import run_lab_helper
from downward.reports.absolute import AbsoluteReport
from lab.environments import BaselSlurmEnvironment, LocalEnvironment
from lab.experiment import Experiment
from lab.reports import Attribute
import numpy as np

# Create custom report class with suitable info and error attributes.
class BaseReport(AbsoluteReport):
    INFO_ATTRIBUTES = ["problem", "time_limit", "memory_limit", "path_length", "solve_time"]
    ERROR_ATTRIBUTES = [
        "domain",
        "problem",
        "unexplained_errors",
        "error",
        "node",
    ]


NODE = platform.node()
REMOTE = NODE.endswith(
    ".scicore.unibas.ch") or NODE.endswith(".cluster.bc2.ch")
SCRIPT_DIR = Path(__file__).parent.absolute()
BENCHMARKS_DIR = SCRIPT_DIR / Path("cp/minizinc/Variants/data/")
FRCSP_INSTANCES = sorted((BENCHMARKS_DIR / "frcsp").glob("*.dzn"))
TCSP_INSTANCES = sorted((BENCHMARKS_DIR / "tcsp").glob("*.dzn"))

SEED = 42
MEMORY_LIMIT = 2048  # MiB
EMAIL = os.environ.get('email', None)
SUITE = FRCSP_INSTANCES

if REMOTE:
    ENV = BaselSlurmEnvironment(email=os.environ['email'])
    TIME_LIMIT = 60  # seconds
else:
    ENV = LocalEnvironment(processes=6)
    # Use lower timeout for local tests.
    TIME_LIMIT = 2  # seconds
ATTRIBUTES = [
    Attribute("path_length", function=max),
    Attribute("solve_time", function=np.mean, digits=5),
    "solver_exit_code",
    Attribute("solved", absolute=True),
]


# Create a new experiment.
exp = Experiment(environment=ENV)
# # Add solver to experiment and make it available to all runs.
# exp.add_resource("solver", os.path.join(SCRIPT_DIR, "solver.py"))
# Add custom parser.
exp.add_parser("parser_lab.py")

runs = []
for problem in FRCSP_INSTANCES[:1]:
    runs.append(run_lab_helper.make_runs(exp, problem, "time_window", TIME_LIMIT, MEMORY_LIMIT))
for problem in FRCSP_INSTANCES[:1]:
    runs.append(run_lab_helper.make_runs(exp, problem, "resource_constrained", TIME_LIMIT, MEMORY_LIMIT))


# Add step that writes experiment files to disk.
exp.add_step("build", exp.build)

# Add step that executes all runs.
exp.add_step("start", exp.start_runs)

# Add step that collects properties from run directories and
# writes them to *-eval/properties.
exp.add_fetcher(name="fetch")

# Make a report.
exp.add_report(BaseReport(attributes=ATTRIBUTES), outfile="report.html")

# Parse the commandline and run the given steps.
exp.run_steps()
