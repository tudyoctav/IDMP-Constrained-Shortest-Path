from graph import Graph, Node
from pysat.pb import PBEnc
from pysat.formula import IDPool
from functools import wraps
from typing import List

def store_clauses(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        res_clauses = method(self, *args, **kwargs)
        if res_clauses == None:
            return res_clauses
        assert all(all(type(x) == int for x in clause)
                   for clause in res_clauses), f"'{method.__name__}' should return a list of clauses or None, but returned: '{res_clauses}'"
        self.clauses.extend(res_clauses)
        return res_clauses
    return wrapper


class ConstraintBuilder(object):

    def __init__(self, graph: Graph, id_pool: IDPool, start=0, end=-1) -> None:
        self.graph = graph
        self.id_pool = id_pool
        nodes = self.graph.get_nodes()
        self.start_node = nodes[start]
        self.end_node = nodes[end]
        self.clauses = []

    def __str__(self) -> str:
        return f"ConstraintBuilder:\ngraph:{self.graph},\nstart, end: {self.start_node}, {self.end_node}".replace("\n", "\n  ")

    @store_clauses
    def start_and_end_constraint(self, start_node: Node = None, end_node: Node = None) -> List[List[int]]:
        if start_node == None:
            start_node = self.start_node
        if end_node == None:
            end_node = self.end_node

        start_constraint = PBEnc.equals([
            self.id_pool.id(edge) for edge in self.graph.edges_of(start_node)
        ], vpool=self.id_pool)
        end_constraint = PBEnc.equals(
            [self.id_pool.id(edge)for edge in self.graph.edges_of(end_node)
             ], vpool=self.id_pool)
        res = [*start_constraint.clauses, *end_constraint.clauses]

        return res

    @store_clauses
    def path_constraint(self, start_node: Node = None, end_node: Node = None) -> List[List[int]]:
        if start_node == None:
            start_node = self.start_node
        if end_node == None:
            end_node = self.end_node
        id_pool = self.id_pool

        res = []
        for node in self.graph.get_nodes():
            if node == start_node or node == end_node:
                continue
            literals = [-id_pool.id(node), *[id_pool.id(edge)
                                             for edge in self.graph.edges_of(node)]]
            weights = [1] * len(literals)
            weights[0] = 2

            res.extend(PBEnc.equals(literals, weights, 2, vpool=id_pool).clauses)
        return res

    @store_clauses
    def max_weight(self, weight_index: int, max_weight: int) -> List[List[int]]:
        id_pool = self.id_pool

        literals = list(map(id_pool.id, self.graph.edges))
        weights = list(map(lambda e: e.weights[weight_index], self.graph.edges))
        
        return PBEnc.atmost(literals, weights, max_weight, vpool=id_pool).clauses
        

    def get_all_clauses(self) -> List[List[int]]:
        return self.clauses
