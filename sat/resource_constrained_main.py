#!/usr/bin/env python
from pysat.solvers import Minisat22, Lingeling
from graph import Graph, Edge, parse_graph
from pysat import formula
from pysat.pb import PBEnc
from optimizer import linear_search, max_sat
import function_constructors
from constraints import ConstraintBuilder
from typing import List, Union
import sys


def run(constraints: formula.CNF, solver=Lingeling) -> Union[List[int],None]:
    print(constraints.clauses)
    with solver(constraints) as solver:
        # print(solver.solve())
        solver.solve()
        return solver.get_model()


def main(file_name):
    with open(file_name, 'r') as graph_file:
        graph = parse_graph(graph_file.read())
    id_pool = formula.IDPool()
    
    constraint_builder = ConstraintBuilder(graph, id_pool, start=0, end=-1)
    constraint_builder.start_and_end_constraint()
    constraint_builder.path_constraint()
    constraint_builder.max_weight(1, 9)

    literals = list(map(id_pool.id, graph.edges))
    weights = list(map(lambda e: e.weights[0], graph.edges))
    # res, val =  linear_search(
    #     formula.CNF(from_clauses=constraint_builder.get_all_clauses()), 
    #     function_constructors.linear(literals, weights, id_pool)
    # )

    res, val = max_sat(formula.CNF(from_clauses=constraint_builder.get_all_clauses()), literals, weights)

    print(f"optimal val is: {val}")
    print_res(res, id_pool)

def sign(a):
    if a < 0:
        return "-"
    else:
        return " "

def print_clauses(formula: formula.CNF, id_pool):
    print("clauses")
    for clause in formula.clauses:
        print(f"  {[sign(var)+ str(id_pool.obj(abs(var))) for var in clause]}")

def print_res(model: Union[List[int], None], id_pool: formula.IDPool):
    if model == None:
        print("problem is infeasible")
        return
    # print(model)
    for v in sorted(model):
        if v > 0 and id_pool.obj(abs(v)) != None:
            print(sign(v) + str(id_pool.obj(abs(v))))

if __name__ == "__main__":
    main(sys.argv[len(sys.argv)- 1])