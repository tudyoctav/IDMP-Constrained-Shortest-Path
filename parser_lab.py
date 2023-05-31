#! /usr/bin/env python

"""
Solver should have the following outputs:

Length: 2
% time elapsed: 0.15 s
"""

from lab.parser import Parser

def solved(content, props):
    props["solved"] = int("path_length" in props)

def error(content, props):
    if props["solved"]:
        props["error"] = "path_found"
    else:
        props["error"] = content

if __name__ == "__main__":
    parser = Parser()
    parser.add_pattern(
        "path length", r"node: (.+)\n", type=str, file="driver.log", required=False
    )
    parser.add_pattern(
        "solver_exit_code", r"solve exit code: (.+)\n", type=int, file="driver.log"
    )
    parser.add_pattern("path_length", r"Length: (\d+)\n", type=int)
    parser.add_pattern("solve_time", r"solveTime=([+-]?([0-9]*[.])?[0-9]+)", type=float, required=True)
    parser.add_function(solved)
    parser.parse()
