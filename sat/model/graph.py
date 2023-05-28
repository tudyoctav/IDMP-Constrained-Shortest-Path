from typing import List
import re

empty_regex=re.compile(r'\s+')
edge_regex=re.compile(r'\d+\s+\d+(\s+\d+)*')
digit_regex = re.compile(r'\d+')

class Node(object):
    def __init__(self, val) -> None:
        self.val = val

    def __str__(self) -> str:
        return f"node_{self.val}"
    
    def __eq__(self, __value: object) -> bool:
        return isinstance(__value, Node) and self.val == __value.val
    
    def __hash__(self):
        return hash(self.val)


class Edge(object):
    def __init__(self, orig: Node, dest: Node, weights=[]) -> None:
        self.orig = orig
        self.dest = dest
        self.weights = weights
    
    def __str__(self) -> str:
        return f"edge: {self.orig} {self.dest} {self.weights}"

    def get_other(self, node: Node):
        """Retrieves the other end node of the edge of the supplied node
        The node should be the node at one of the ends of the edge.
        """
        assert node == self.orig or node == self.dest
        if node == self.orig:
            return self.dest
        else:
            return self.orig

class Graph(object):
    def __init__(self, n_nodes: int, edges: List[Edge]) -> None:
        self.n_nodes = n_nodes
        self.n_edges = len(edges)
        self.edges = edges
        
    
    def __str__(self) -> str:
        res = "graph object\n"
        res += f"  number of nodes: '{self.n_nodes}'"
        for edge in self.edges:
            edge_str = str(edge).replace("\n", "\n    ")
            res += f"\n    {edge_str}"
        return res

    def edges_of(self, id: Node) -> List[Edge]:
        assert id.val >= 0 and id.val < self.n_nodes, f"The id '{id}' is not valid for the interval [{0},{self.n_nodes})"
        res = []
        for edge in self.edges:
            if edge.orig == id:
                res.append(edge)
            elif edge.dest == id:
                res.append(edge)
        return res

            

    def neighs_of(self, id: Node) -> List[Node]:
        res = []
        for edge in self.edges_of(id):
            if edge.orig == id:
                res.append(edge.dest)
            else: 
                assert edge.dest == id
                res.append(edge.orig)
        return res

    def get_nodes(self) -> List[Node]:
        return [Node(i) for i in range(self.n_nodes)]


def parse_graph(inp: str):
    split = inp.splitlines()
    split_it = iter(split)
    n_nodes, n_edges = map(int, digit_regex.findall(next(split_it)))
    edges = []
    for line,_ in zip(split_it, range(n_edges)):
        if empty_regex.match(line):
            continue
        edges.append(parse_edge(line))
    assert len(edges) == n_edges
    return Graph(n_nodes, edges)

def parse_edge(line: str) -> Edge:
    assert edge_regex.fullmatch(line), f"Incorrect format in: '{line}' expected: '{edge_regex.pattern}'"
    it = iter(digit_regex.findall(line))
    it = map(int, it)
    return Edge(Node(next(it)), Node(next(it)), list(it))
    




    