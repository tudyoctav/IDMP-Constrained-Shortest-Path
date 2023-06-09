from graph import Graph, Node
from pysat.pb import PBEnc
from pysat.formula import IDPool
from functools import wraps
from typing import List, Tuple

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
            self.id_pool.id(edge) for edge in self.graph.edges_from(start_node)
        ], vpool=self.id_pool)
        end_constraint = PBEnc.equals(
            [self.id_pool.id(edge)for edge in self.graph.edges_to(end_node)
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
            # if node -> 1 outgoing edge
            from_literals = [-id_pool.id(node), *[id_pool.id(edge)
                                             for edge in self.graph.edges_from(node)]]
            to_literals = [-id_pool.id(node), *[id_pool.id(edge) for edge in self.graph.edges_to(node)]]
            res.extend(PBEnc.equals(from_literals, vpool=id_pool).clauses)
            res.extend(PBEnc.equals(to_literals, vpool=id_pool).clauses)
        return res

    @store_clauses
    def max_weight(self, weight_index: int, max_weight: int) -> List[List[int]]:
        id_pool = self.id_pool

        literals = list(map(id_pool.id, self.graph.edges))
        weights = list(map(lambda e: e.weights[weight_index], self.graph.edges))
        print("w:", weights)
        assert all(w >= 0 for w in weights), "Edge weights should be possitive"
        
        if max_weight < 0 or max_weight > sum(weights):
            return []

        return PBEnc.atmost(literals, weights, max_weight, vpool=id_pool).clauses
        
    @store_clauses
    def min_weight(self, weight_index: int, min_weight: int) -> List[List[int]]:
        id_pool = self.id_pool
        if min_weight <= 0:
            return []

        literals = list(map(id_pool.id, self.graph.edges))
        weights = list(map(lambda e: e.weights[weight_index], self.graph.edges))
        
        return PBEnc.atleast(literals, weights, min_weight, vpool=id_pool).clauses

    def limit_weight_list(self, weights_lim: List[Tuple[int, int]]):
        # Note cluasus are stored in the max/min weight function so no need to store them here!
        res = []
        for i, (min_weight, max_weight) in enumerate(weights_lim):
            res.extend(self.min_weight(i+1, min_weight))
            res.extend(self.max_weight(i+1, max_weight))
        return res


    def get_all_clauses(self) -> List[List[int]]:
        return self.clauses
