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
    # constraint_builder.channeling()
    constraint_builder.connected()
    constraint_builder.node_order()
    constraint_builder.start_and_end_constraint()
    constraint_builder.visit_one_at_a_time()
    constraint_builder.visit_nodes_only_once()
    # constraint_builder.stop_at_end()
    constraint_builder.enforce_time_windows()

    # literals = list(map(id_pool.id, graph.edges))
    # weights = list(map(lambda e: e.weights[0], graph.edges))
    literals = constraint_builder.get_optim_literals()
    weights = [1 for _ in literals]
    clauses = constraint_builder.get_all_clauses()
    # clauses += [[id_pool.id(constraint_builder.route_var[-2][-1])]]
    res, val = max_sat(formula.CNF(from_clauses=clauses), literals, weights)

    print(f"optimal val is: {val}")
    print_res(res, id_pool)

def main(file_name):
    with open(file_name, 'r') as graph_file:
        graph = parse_graph_with_time(graph_file.read())
    run(graph)

if __name__ == "__main__":
    main(sys.argv[len(sys.argv)- 1])