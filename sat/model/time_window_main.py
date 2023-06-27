#!/usr/bin/env python
from time_graph import parse_graph_with_time, TimeGraph
from time_constraint import TimeConstraintBuilder
from pysat.formula import IDPool
from pysat import formula
import sys
from resource_constrained_main import print_res
from optimizer import max_sat
from pathlib import Path
from typing import Union
import re
import time_graph
from graph import Graph, Edge, Node
from parse_dzn import get_par

def parse_dzn(inp: str) -> TimeGraph:
    n = get_par(inp, "N")
    m = get_par(inp, "M")
    edge_start = get_par(inp, "Edge_Start")
    edge_end = get_par(inp, "Edge_End")
    l = get_par(inp, "L")
    t = get_par(inp, "T")
    lower_bound = get_par(inp, "Lower_Bound")
    upper_bound = list(map(lambda x: x + 1, get_par(inp, "Upper_Bound")))
    edges = [Edge(Node(start - 1), Node(end - 1), [length, time]) for (start, end, length, time) in zip(edge_start, edge_end, l, t)]
    graph = Graph(n, edges)
    graph = time_graph.time_graph_from_graph(graph, list(zip(lower_bound, upper_bound)))
    print(graph)
    for n in graph.nodes:
        print(n, n.lower_bound, n.upper_bound)
    return graph

def parse_file(file_name: Union[Path,str]):
    file_name = Path(file_name)
    with open(file_name) as file:
        inp = file.read()
    if file_name.suffix == ".txt":
        return parse_graph_with_time(inp)
    elif file_name.suffix == ".dzn":
        return parse_dzn(inp)
    else:
        raise AssertionError("unkown file type")

def run(graph: TimeGraph, solver:str):
    id_pool = IDPool()
    constraint_builder = TimeConstraintBuilder(graph, id_pool)
    constraint_builder.channeling()
    constraint_builder.connected()
    constraint_builder.node_order()
    constraint_builder.start_and_end_constraint()
    constraint_builder.visit_one_at_a_time()
    constraint_builder.visit_nodes_only_once()
    constraint_builder.stop_at_end()
    constraint_builder.enforce_time_windows()

    literals = list(map(id_pool.id, graph.edges))
    weights = list(map(lambda e: e.weights[0], graph.edges))
    # literals = constraint_builder.get_optim_literals()
    # weights = [1 for _ in literals]
    clauses = constraint_builder.get_all_clauses()
    res, val = max_sat(formula.CNF(from_clauses=clauses), literals, weights, solver)

    print(f"optimal val is: {val}")
    print_res(res, id_pool)
    if val == None:
        exit(1)

def main(file_name, solver="cadical153"):
    graph = parse_file(file_name)
    run(graph, solver)

if __name__ == "__main__":
    main(sys.argv[len(sys.argv)- 1])