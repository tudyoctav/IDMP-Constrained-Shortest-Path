from graph import Graph
from time_graph import TimeGraph
from pysat.formula import IDPool
from pysat.pb import PBEnc
from constraints import store_clauses, ConstraintBuilder
from typing import List

class TimeConstraintBuilder(ConstraintBuilder):

    def __init__(self, graph: TimeGraph, id_pool: IDPool, start=0, end=-1) -> None:
        super().__init__(graph, id_pool, start, end)
        nodes = self.graph.get_nodes()
        self.route_var = [[(i,n) for n in graph.get_nodes()] for i in range(graph.n_nodes)]

    def visit_once_index(self, i: int):
        graph = self.graph
        id_pool = self.id_pool

        node_options = self.route_var[i]
        node_vars = map(id_pool.id, node_options)
        return PBEnc.equals(node_vars, vpool=id_pool).clauses

    # @store_clauses
    # def visit_once(self):
    #     graph = self.graph
    #     id_pool = self.id_pool
        
    #     clauses = []
    #     for i in range(1, len(self.route_var)):
    #         clauses.extend(self.visit_once_index(i))
    #     return clauses
    
    # @store_clauses
    # def start_and_end_constraint(self, start_node: int = None, end_node: int = None) -> List[List[int]]:
    #     if start_node == None:
    #         start_node = self.start_node.val
    #     if end_node == None:
    #         end_node = self.end_node.val
    #     id_pool = self.id_pool

    #     clauses = [
    #         [id_pool.id(self.route_var[0][start_node])],
    #         [id_pool.id(self.route_var[-1][end_node])],
    #     ]
        
    #     return clauses
    
    # @store_clauses
    # def visit_all_once(self, end_node: int = None):
    #     if end_node == None:
    #         end_node = self.end_node
        
    #     clauses = []
    #     for node_id in range(self.graph.n_nodes):
    #         if node_id == end_node.val:
    #             continue
    #         curent_node_vars = [self.id_pool.id(l[node_id]) for l in self.route_var]
    #         clauses.extend(PBEnc.equals(curent_node_vars, vpool=self.id_pool).clauses)
    #     return clauses

    @store_clauses
    def stop_at_end(self, end_node: int = None):
        """enforces that when the end node is reached we don't look further
        Is likely redundand since adding more nodes would just add additional path length.
        But likely reduces the amount of times to solve
        """
        if end_node == None:
            end_node = self.end_node.val
        
        clauses = []

        for path_index in range(1, len(self.route_var)):
            previous = self.id_pool.id(self.route_var[path_index - 1][end_node])
            current = self.id_pool.id(self.route_var[path_index][end_node])

            # If previous -> current, meaning if the previous node was the end the current node is also the end.
            clauses.append([-previous, current])
        return clauses
    
    @store_clauses
    def channeling(self):
        res = []
        for step in self.route_var:
            for i, n in step:
                path_var = self.id_pool.id((i,n))
                node_var = self.id_pool.id(n)
                res.append([-path_var, node_var])
                res.append([path_var, -node_var])

    @store_clauses
    def connected(self):
        start_node = self.start_node
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

    #         res.extend(PBEnc.equals(literals, weights, 2, vpool=id_pool).clauses)
    #     return res

    