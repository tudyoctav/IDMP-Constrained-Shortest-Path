from pathlib import Path
import time_window_main
import resource_constrained_main
import sys
import argparse

TW_KEY = "time_window"
RC_KEY = "resource_constraint"

def init_arg_parse(args=None):
    parser = argparse.ArgumentParser(
        description='Solver runner for time_window and resource_constrained Shortest Path problems ')
    parser.add_argument("problem_type", help="The problem type to solve.", choices=[
                        RC_KEY, TW_KEY])
    parser.add_argument("file_name", type=Path,
                        help="The instance file to run.")
    parser.add_argument("-s", "--solver", dest="solver", type=str,
                        help="The name of the solver to use.", default="cadical153")
    return vars(parser.parse_args(args))


if __name__ == "__main__":
    vargs =init_arg_parse()
    if vargs["problem_type"] == 'time_window':
        del vargs["problem_type"]
        time_window_main.main(**vargs)
        sys.exit()
    elif sys.argv[1] == 'resource_constraint':
        del vargs["problem_type"]
        resource_constrained_main.main(**vargs)
        sys.exit()
    raise NotImplementedError()
        