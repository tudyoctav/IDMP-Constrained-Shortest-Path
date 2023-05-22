#!/usr/bin/env python
from time_graph import parse_graph_with_time, TimeGraph
from time_constraint import TimeConstraintBuilder
from pysat.formula import IDPool
from pysat import formula
import sys
from resource_constrained_main import print_res
from optimizer import max_sat

def run(graph: TimeGraph):
    id_pool = IDPool()
    constraint_builder = TimeConstraintBuilder(graph, id_pool)
    constraint_builder.channeling()
    constraint_builder.connected()
    constraint_builder.start_and_end_constraint()
    constraint_builder.path_constraint()
    constraint_builder.stop_at_end()
    constraint_builder.path_constraint()

    literals = list(map(id_pool.id, graph.edges))
    weights = list(map(lambda e: e.weights[0], graph.edges))
    res, val = max_sat(formula.CNF(from_clauses=constraint_builder.get_all_clauses()), literals, weights)

    print(f"optimal val is: {val}")
    print_res(res, id_pool)

def main(file_name):
    with open(file_name, 'r') as graph_file:
        graph = parse_graph_with_time(graph_file.read())
    run(graph)

if __name__ == "__main__":
    main(sys.argv[len(sys.argv)- 1])