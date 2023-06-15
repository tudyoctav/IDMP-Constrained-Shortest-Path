#! /usr/bin/env python

"""
Solver should have the following outputs:

Length: 2
% time elapsed: 0.15 s
"""

from lab.parser import Parser
from pathlib import Path

def solved(content, props):
    props["solved"] = int("path_length" in props)

ERROR_VALUE = None

def timed_out(content, props):
    props["path_length"] = ERROR_VALUE
    props["solve_time"] = ERROR_VALUE

if __name__ == "__main__":
    parser = Parser()
    parser.add_pattern(
        "node", r"node: (.+)\n", type=str, file="driver.log", required=True
    )
    parser.add_pattern(
        "solver_exit_code", r"solve exit code: (.+)\n", type=int, file="driver.log", required=True
    )
    if Path("run.log").exists():
        parser.add_pattern("path_length", r"(?:Length: |optimal val is: )(\d+)\n", type=int, required=False)
        parser.add_pattern("solve_time", r"solveTime=([-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?)", type=float, required=False)
    else:
        parser.add_function(timed_out, "driver.log")
    parser.add_function(solved, "driver.log")
    parser.parse()
