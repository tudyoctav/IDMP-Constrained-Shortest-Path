from typing import List
from graph import Graph, parse_graph, digit_regex, Node
import re
from typing import Tuple, List 

from graph import Edge, Node

time_window_regex=re.compile(r"\d+\s+\d+\s*")   

class TimeNode(Node):
    def __init__(self, val, lower_bound, upper_bound):
        super(TimeNode, self).__init__(val)
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
    
    def __repr__(self) -> str:
        return f"TimeNode({self.val},{self.lower_bound},{self.upper_bound})"
    
    
def add_window_to_node(node: Node, lower_bound:int, upper_bound:int) -> TimeNode:
    return TimeNode(node.val, lower_bound, upper_bound)
    

class TimeGraph(Graph):

    def get_nodes(self) -> List[TimeNode]:
        return self.nodes

    def __init__(self, nodes: List[Node], edges: List[Edge], windows: List[Tuple[int, int]]) -> None:
        super(TimeGraph, self).__init__(len(nodes), edges)
        base_nodes = super().get_nodes()
        self.nodes = nodes

        
def time_graph_from_graph(graph: Graph, windows: List[Tuple[int, int]]):
    n_nodes = graph.n_nodes
    assert n_nodes == len(windows), f"the number of windows: {len(windows)} should equal the number of nodes: {n_nodes}"
    nodes = [add_window_to_node(Node(i), *windows[i]) for i in range(n_nodes)]
    edges = [Edge(nodes[edge.orig.val], nodes[edge.dest.val], edge.weights) for edge in graph.edges]
    return TimeGraph(nodes, edges, windows)        

def parse_graph_with_time(inp: str):
    graph = parse_graph(inp)
    start_index = graph.n_edges + 1
    end_index = start_index + graph.n_edges
    windows = []
    for line in inp.splitlines()[start_index: end_index]:
        assert time_window_regex.fullmatch(line), f"expected a time window but found: '{line}'"
        windows.append(digit_regex.findall(line))
    return time_graph_from_graph(graph, windows)
    