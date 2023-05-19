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
    
def add_window_to_node(node: Node, lower_bound:int, upper_bound:int) -> TimeNode:
    return TimeNode(node.val, lower_bound, upper_bound)
    

class TimeGraph(Graph):

    def get_nodes(self) -> List[TimeNode]:
        return self.nodes

    def __init__(self, n_nodes: int, edges: List[Edge], windows: List[Tuple[int, int]]) -> None:
        super(TimeGraph, self).__init__(n_nodes, edges)
        base_nodes = super().get_nodes()
        assert n_nodes == len(windows), f"the number of windows: {len(windows)} should equal the number of nodes: {n_nodes}"
        self.nodes = [add_window_to_node(base_nodes[i], *windows[i]) for i in range(n_nodes)]

        
def time_graph_from_graph(graph: Graph, windows: List[Tuple[int, int]]):
    n_nodes = graph.n_nodes
    edges = graph.edges
    return TimeGraph(n_nodes, edges, windows)        

def parse_graph_with_time(inp: str):
    graph = parse_graph(inp)
    start_index = graph.n_edges + 1
    end_index = start_index + graph.n_edges
    [print(e) for e in graph.edges]
    windows = []
    for line in inp.splitlines()[start_index: end_index]:
        assert time_window_regex.fullmatch(line), f"expected a time window but found: '{line}'"
        windows.append(digit_regex.findall(line))
    return time_graph_from_graph(graph, windows)
    