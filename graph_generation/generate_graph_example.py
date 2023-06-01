import matplotlib
import tempfile
import os
import sys

sys.path.append("../")

from pygraphml import GraphMLParser
from pygraphml import Graph

g = Graph()

# Add nodes
n1 = g.add_node(0)
n2 = g.add_node(1)
n3 = g.add_node(2)
n4 = g.add_node(3)
n5 = g.add_node(4)

# Add edges
e1 = g.add_edge(n1, n3)
e2 = g.add_edge(n2, n3)
e3 = g.add_edge(n3, n4)
e4 = g.add_edge(n3, n5)

# Add node attributes

n1["lower_bound"] = 0
n2["lower_bound"] = 0
n3["lower_bound"] = 0
n4["lower_bound"] = 0
n5["lower_bound"] = 0

n1["upper_bound"] = 20
n2["upper_bound"] = 20
n3["upper_bound"] = 20
n4["upper_bound"] = 20
n5["upper_bound"] = 20


# Add edge attributes
e1["weight"] = 10
e2["weight"] = 5
e3["weight"] = 3
e4["weight"] = 2

e1["time"] = 15
e2["time"] = 10
e3["time"] = 5
e4["time"] = 2


# Set a root
g.set_root(n1)

nodes = g.BFS()
for node in nodes:
    print(node)

nodes = g.DFS_prefix()
for node in nodes:
    print(node)
# fname = tempfile.mktemp()
fname = "graphs/basic-graph.graphml"
parser = GraphMLParser()
parser.write(g, fname)
with open(fname) as f:
    print(f.read())

g.show()

