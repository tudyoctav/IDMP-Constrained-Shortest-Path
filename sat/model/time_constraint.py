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
        self.optim_variables = None

    def visit_one_at_a_time_index(self, i: int):
        graph = self.graph
        n_nodes = self.graph.n_nodes
        id_pool = self.id_pool

        node_options = self.route_var[i]
        node_vars = list(map(id_pool.id, node_options))
        return PBEnc.equals(node_vars, vpool=id_pool).clauses

    @store_clauses
    def visit_one_at_a_time(self):
        clauses = []
        for i in range(self.graph.n_nodes):
            clauses.extend(self.visit_one_at_a_time_index(i))
        return clauses
    
    @store_clauses
    def start_and_end_constraint(self, start_node: int = None, end_node: int = None) -> List[List[int]]:
        if start_node == None:
            start_node = self.start_node.val
        if end_node == None:
            end_node = self.end_node.val
        id_pool = self.id_pool

        clauses = [
            [id_pool.id(self.route_var[0][start_node])],
            [id_pool.id(self.route_var[-1][end_node])],
        ]
        
        return clauses
    
    @store_clauses
    def visit_nodes_only_once(self, end_node: int = None):
        if end_node == None:
            end_node = self.end_node
        
        clauses = []
        for node_id in range(self.graph.n_nodes):
            if node_id == end_node.val:
                continue
            curent_node_vars = [self.id_pool.id(l[node_id]) for l in self.route_var]
            clauses.extend(PBEnc.leq(curent_node_vars, vpool=self.id_pool).clauses)
        return clauses

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
                # res.append([path_var, -node_var])
        return res


    @store_clauses
    def connected(self):
        start_node = self.start_node
        end_node = self.end_node
        id_pool = self.id_pool

        res = []
        for node in self.graph.get_nodes():
            edge_lits = [id_pool.id(edge) for edge in self.graph.edges_of(node)]
            if node == start_node or node == end_node:
                assert len(edge_lits) > 0, "The start and end node should be connected"
                res.extend(PBEnc.equals(edge_lits, bound=1, vpool=id_pool))
            else:
                # node_lits  = [id_pool.id(self.route_var[i][node.val]) for i in range(self.graph.n_nodes)]
                node_lits = [-id_pool.id(node)]
                literals = edge_lits + node_lits
                weights = [1 for _ in edge_lits] + [2 for _ in node_lits]
                res.extend(PBEnc.equals(literals, weights, 2, vpool=id_pool))
        return res
    
    @store_clauses
    def node_order(self):
        id_pool = self.id_pool
        res_cluases = []

        for step_index in range(0, len(self.route_var)):
            for node in self.graph.get_nodes():
                if node == self.end_node:
                    continue
                node_lit = id_pool.id((step_index, node))
                for edge in self.graph.edges_of(node):
                    edge_lit = id_pool.id(edge)
                    other_node = edge.get_other(node)
                    next_node_lit = id_pool.id((step_index + 1, other_node))
                    if node == self.start_node:
                        res_cluases.append([-node_lit, -edge_lit, next_node_lit])
                    else:
                        prev_node_lit = id_pool.id((step_index - 1, other_node))
                        # If the current node is used than the previous or the next node is on the edge
                        res_cluases.append([-node_lit, -edge_lit, prev_node_lit, next_node_lit])


        return res_cluases

    def get_max_path_length(self):
        """Returns a upperbound for the maximum time traversing the graph could take
        Note that this does not necesarily mean that the longest path is as long as start to finish
        """
        return self.end_node.upper_bound

    @store_clauses
    def enforce_time_windows(self):
        id_pool = self.id_pool
        n_nodes = self.graph.n_nodes
        max_length = self.get_max_path_length()
        all_clauses = []
        prev_variables = []
        current_variables = []
        for step_index in range(1,n_nodes):
            cur_clauses = []
            vars = []
            weights = []
            
            # is_edge_current_taken = [(edge, id_pool._next()) for edge in self.graph.edges]
            for node in self.graph.get_nodes():
                cur_node  = id_pool.id(self.route_var[step_index  ][node.val])

                for edge in self.graph.edges_of(node):
                    other_node = edge.get_other(node)
                    prev_node = id_pool.id(self.route_var[step_index-1][other_node.val])
                    edge_used = id_pool.id(f"edge'{node.val}, {other_node.val}' used at:{step_index}")
                    vars.append(edge_used)
                    weights.append(edge.weights[1])
                    # if current_node /\ prev_node -> egde is used
                    cur_clauses.append(
                        [-cur_node, -prev_node, edge_used]
                    )
            assert len(vars) == len(weights)
            prev_variables = current_variables
            current_variables = [id_pool.id(f"weight at:{step_index}:{i}") for i in range(max_length)]
            # Force upper and lower bound
            for var in self.route_var[step_index]:
                node = var[1]
                var = id_pool.id(var)
                # lower_bound_clauses = [[-var, *clause] for clause in PBEnc.leq(current_variables, bound=node.lower_bound, vpool=id_pool)]
                lower_bound_clauses = []
                for index, unary_literal in enumerate(current_variables):
                    if index >= node.lower_bound:
                        break
                    lower_bound_clauses.append([-var, unary_literal])
                cur_clauses.extend(lower_bound_clauses)
                upper_bound_clauses = [[-var, *clause] for clause in PBEnc.leq(current_variables, bound=node.upper_bound - 1, vpool=id_pool)]
                cur_clauses.extend(upper_bound_clauses)
            vars.extend(prev_variables)
            weights.extend([1 for _ in prev_variables])
            assert len(vars) == len(weights)
            # Sum previous path length with current and the edge used:
            for index, cur_var in enumerate(current_variables):
                constraint = PBEnc.leq(vars, weights, index, vpool=id_pool)
                new_clauses = [[*clause, cur_var] for clause in constraint.clauses]
                cur_clauses.extend(new_clauses)
            all_clauses.extend(cur_clauses)
        self.optim_variables = current_variables
        return all_clauses

    def get_optim_literals(self):
        assert self.optim_variables != None, "The optimization variables were not set make sure you call enforce_time_windows first"
        return self.optim_variables

    #         res.extend(PBEnc.equals(literals, weights, 2, vpool=id_pool).clauses)
    #     return res

    