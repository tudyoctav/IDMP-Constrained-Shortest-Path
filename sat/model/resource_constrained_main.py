#!/usr/bin/env python
from pysat.solvers import Minisat22, Lingeling
from graph import Graph, Edge, Node, parse_graph
from pysat import formula
from pysat.pb import PBEnc
from optimizer import linear_search, max_sat
import function_constructors
from constraints import ConstraintBuilder
from typing import List, Tuple, Union
import sys
from parse_dzn import get_par
from pathlib import Path

def parse_dzn(inp: str) -> Tuple[Graph, list]:
    n = get_par(inp, "N")
    m = get_par(inp, "M")
    edge_start = get_par(inp, "Edge_Start")
    edge_end = get_par(inp, "Edge_End")
    l = get_par(inp, "L")
    t = get_par(inp, "T")
    weights_max = [get_par(inp, "Time")]
    weights_min = [0]
    weights_lim = list(zip(weights_min, weights_max))
    edges = [Edge(Node(start - 1), Node(end - 1), [length, time]) for (start, end, length, time) in zip(edge_start, edge_end, l, t)]
    [print(e) for e in edges]
    graph = Graph(n, edges)
    
    return graph, weights_lim

def parse_file(file_name: Union[Path,str]):
    file_name = Path(file_name)
    with open(file_name) as file:
        inp = file.read()
    match file_name.suffix:
        case ".txt":
            raise NotImplementedError()
            return parse_graph(inp)
        case ".dzn":
            return parse_dzn(inp)
        case _:
            raise AssertionError("unkown file type")


def run(constraints: formula.CNF, solver=Lingeling) -> Union[List[int],None]:
    print(constraints.clauses)
    with solver(constraints) as solver:
        # print(solver.solve())
        solver.solve()
        return solver.get_model()


def main(file_name, solver="cadical153"):
    graph,weights_lim = parse_file(file_name)
    id_pool = formula.IDPool()
    
    constraint_builder = ConstraintBuilder(graph, id_pool, start=0, end=-1)
    constraint_builder.start_and_end_constraint()
    constraint_builder.path_constraint()
    constraint_builder.limit_weight_list(weights_lim)

    literals = list(map(id_pool.id, graph.edges))
    weights = list(map(lambda e: e.weights[0], graph.edges))
    # res, val =  linear_search(
    #     formula.CNF(from_clauses=constraint_builder.get_all_clauses()), 
    #     function_constructors.linear(literals, weights, id_pool)
    # )

    res, val = max_sat(formula.CNF(from_clauses=constraint_builder.get_all_clauses()), literals, weights, solver)

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