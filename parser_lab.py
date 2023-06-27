#! /usr/bin/env python

"""
Solver should have the following outputs:

Length: 2
% time elapsed: 0.15 s
"""

import re
import sys
from lab.parser import Parser
from pathlib import Path


def solved(content, props):
    if "=====UNKNOWN=====" in content:
        # Minizinc timed out
        timed_out(content, props)
    else:
        props["solved"] = int(props.get("solve_time", None) != None)


ERROR_VALUE = None
PROBLEM_KEY = "domain"
PROBLEM_NAME_RE = re.compile(r"\"problem\": \"(.*)\"")
STATIC_PROP_FILE = "static-properties"
with open(STATIC_PROP_FILE) as f:
    PROBLEM_NAME = PROBLEM_NAME_RE.search(f.read()).group(1)


def timed_out(content, props):
    props["path_length"] = ERROR_VALUE
    props["solve_time"] = ERROR_VALUE
    props["solved"] = 0


GEN_METHOD_REGEX = re.compile(r"([A-Za-z0-9]+_[A-Za-z0-9]+)")
CITY_SIZE = re.compile(r"()")

def parse_gen_method(content, props):
    problem_name = PROBLEM_NAME.replace("_The_Hague_", "_The-Hague_")
    problem_name = PROBLEM_NAME.replace("_Delft_NL_180_240_2", "_Delft_NL_60_120_2")
    gen_method = GEN_METHOD_REGEX.match(problem_name)
    if gen_method == None:
        props["generation method"] = None
        return
    gen_method = gen_method[0]
    if gen_method == "hexagonal_lattice":
        gen_method = "hexagonal lattice"
    else:
        props["city"] = gen_method.split("_")[1]
        gen_method = "open maps"
        sizes = {
            "_60_120_": "small",
            "_120_180_": "medium",
            "_180_240_": "large",
            "_240_300_": "huge",
        }
        for s, size in sizes.items():
            if s in problem_name:
                props["city size"] = size
    props["generation method"] = gen_method


N_REGEX = re.compile(r"_N_([0-9]+)")


def parse_n(content, props):
    N = N_REGEX.search(PROBLEM_NAME)
    if N != None:
        N = int(N[1])
    else:
        N = -1
    props["N"] = N


WEIGHTS_REGEX = re.compile(r"_weights-([A-Za-z0-9]+)|([A-Za-z0-9]+)_weights\.")
def parse_weights_gen(content, props):
    weight_generation = WEIGHTS_REGEX.search(PROBLEM_NAME)
    if weight_generation != None:
        weight_generation = weight_generation[1]
    props["weight generation"] = weight_generation


WINDOW_REGEX = re.compile(r"_windows-([A-Za-z0-9]+)")
def parse_window_gen(content, props):
    window_generation = WINDOW_REGEX.search(PROBLEM_NAME)
    if window_generation != None:
        window_generation = window_generation[1]
    props["window generation"] = window_generation

PENALTY_REGEX = re.compile(r"_penalty-([A-Za-z0-9]+)_")
def parse_penalty_gen(content, props):
    penalty_generation = PENALTY_REGEX.search(PROBLEM_NAME)
    if penalty_generation != None:
        penalty_generation = penalty_generation[1]
    props["penalty generation"] = penalty_generation

TASK_REGEX = re.compile(r"_([A-Za-z0-9]+)-path")
def parse_task_gen(content, props):
    task_generation = TASK_REGEX.search(PROBLEM_NAME)
    if task_generation != None:
        task_generation = task_generation[1]
    props["task generation"] = task_generation


PROPERTIES_FILE = "static-properties"
if __name__ == "__main__":
    parser = Parser()
    parser.add_pattern(
        "node", r"node: (.+)\n", type=str, file="driver.log", required=True
    )
    parser.add_pattern(
        "solver_exit_code", r"solve exit code: (.+)\n", type=int, file="driver.log", required=True
    )
    if Path("run.log").exists():
        REGEX = r"(?:Length: |optimal val is: |The length of the CSP is |best objective value:\s+)(\d+)\n"
        parser.add_pattern("path_length", REGEX, type=int, required=False)
        SOLVE_RE = r"(?:solveTime=|Total\s\(root\+branch&cut\)\s=\s+)([-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?)"
        parser.add_pattern("solve_time", SOLVE_RE, type=float, required=False)
        parser.add_function(solved, "run.log")
    else:
        parser.add_function(timed_out, PROPERTIES_FILE)
    parser.add_function(parse_gen_method, PROPERTIES_FILE)
    parser.add_function(parse_n, PROPERTIES_FILE)
    parser.add_function(parse_weights_gen, PROPERTIES_FILE)
    parser.add_function(parse_window_gen, PROPERTIES_FILE)
    parser.add_function(parse_penalty_gen, PROPERTIES_FILE)
    parser.add_function(parse_task_gen, PROPERTIES_FILE)

    parser.parse()
