#!/usr/bin/env python
from pysat.solvers import Minisat22, Lingeling
from graph import Graph, Edge, parse_graph
from pysat import formula
from pysat.pb import PBEnc
from optimizer import linear_search
import function_constructors

import sys


def run(constraints: formula.CNF, solver=Lingeling) -> list[int] | None:
    print(constraints.clauses)
    with solver(constraints) as solver:
        # print(solver.solve())
        solver.solve()
        return solver.get_model()


def main(file_name):
    with open(file_name, 'r') as graph_file:
        graph = parse_graph(graph_file.read())
    id_pool = formula.IDPool()
    node_vars = [node for node in graph.get_nodes()]
    edge_vars = [edge for edge in graph.edges]
    start_node = node_vars[0]
    end_node = node_vars[-1]
    # print(graph)

    constraint_list = [
        # add constraint for start node
        *PBEnc.equals([id_pool.id(edge) for edge in graph.edges_of(start_node)], vpool=id_pool).clauses,
        # add constraint for end node
        *PBEnc.equals([id_pool.id(edge) for edge in graph.edges_of(end_node)], vpool=id_pool).clauses,
    ]

    

    for node in graph.get_nodes():
        if node == start_node or node == end_node:
            continue
        literals = [-id_pool.id(node), *[id_pool.id(edge) for edge in graph.edges_of(node)]]
        weights = [1] * len(literals)
        weights[0] = 2
        constraint_list.extend(
            PBEnc.equals(literals, weights, 2, vpool=id_pool).clauses
        )

    max_weight = 9
    literals = list(map(id_pool.id, graph.edges))
    weights = list(map(lambda e: e.weights[1], graph.edges))
    constraint_list.extend(
        PBEnc.atmost(literals, weights, max_weight, vpool=id_pool).clauses
    )

    # res = run(formula.CNF(from_clauses=constraint_list))
    # res, val =  linear_search(
    #     formula.CNF(from_clauses=constraint_list), 
    #     function_constructors.sum([id_pool.id(n) for n in graph.edges])
    # )
    literals = list(map(id_pool.id, graph.edges))
    weights = list(map(lambda e: e.weights[0], graph.edges))
    res, val =  linear_search(
        formula.CNF(from_clauses=constraint_list), 
        function_constructors.linear(literals, weights, id_pool)
    )

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

def print_res(model: list[int] | None, id_pool: formula.IDPool):
    if model == None:
        print("problem is infeasible")
        return
    # print(model)
    for v in model:
        if v > 0 and id_pool.obj(abs(v)) != None:
            print(sign(v) + str(id_pool.obj(abs(v))))

if __name__ == "__main__":
    main(sys.argv[len(sys.argv)- 1])