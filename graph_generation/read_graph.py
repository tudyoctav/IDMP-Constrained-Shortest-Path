import matplotlib
import tempfile
import glob
import os
import sys

sys.path.append("../")

from pygraphml import GraphMLParser
from pygraphml import Graph

def create_minizinc_dzn_file(graphml_obj, filename):
    # Extract necessary information from the graphml_obj
    N = len(graphml_obj.nodes())
    M = len(graphml_obj.edges())
    Edge_Start = []
    Edge_End = []
    L = []
    T = []
    Lower_Bound = []
    Upper_Bound = []
    for edge in graphml_obj.edges():
        Edge_Start.append(int(edge.node1.id) + 1)
        Edge_End.append(int(edge.node2.id) + 1) 
        L.append(int(edge['weight']))  
        T.append(int(edge['time'])) 

    for node in graphml_obj.nodes():
        Lower_Bound.append(int(node["lower_bound"]))  
        Upper_Bound.append(int(node["upper_bound"]))

    # Write the extracted information to the MiniZinc .dzn file
    with open(filename, 'w') as f:
        f.write(f'N = {N};\n')
        f.write(f'M = {M};\n')
        f.write(f'Edge_Start = {Edge_Start};\n')
        f.write(f'Edge_End = {Edge_End};\n')
        f.write(f'L = {L};\n')
        f.write(f'T = {T};\n')
        f.write(f'Lower_Bound = {Lower_Bound};\n')
        f.write(f'Upper_Bound = {Upper_Bound};\n')
        f.write(f'Start = 1;\n')
        f.write(f'End = {N};\n')
        f.write(f'Time = {sum(T)};\n')

files = glob.glob(f"./graphs/**.graphml")
# fname = "graphs/basic-graph.graphml"
parser = GraphMLParser()
for fname in files:
    print(fname)
    graph = parser.parse(fname)
    create_minizinc_dzn_file(graph, fname.replace('.graphml', '.dzn').replace('graphs', 'data/cp'))
    # graph.show()