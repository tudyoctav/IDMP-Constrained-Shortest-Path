import networkx as nx
import matplotlib
import tempfile
import random
import glob
import sys
import os
import numpy as np
import matplotlib.pyplot as plt

sys.path.append("../")

from pygraphml import GraphMLParser
from pygraphml import Graph

def create_data_file_tcsp(graph, filename):
    if not nx.is_directed(graph):
        graph = graph.to_directed()
    # Extract necessary information from the graphml_obj
    N = len(graph.nodes())
    M = len(graph.edges())
    Start = graph.graph['start_node']
    End = graph.graph['finish_node']
    tasks = {}
    num_tasks = graph.graph["num_tasks"]
    num_of_nodes = graph.graph["num_of_nodes_per_task"]
    Edge_Start = []
    Edge_End = []
    lenghts = []
    for node in graph.nodes():
        if "task" in graph.nodes[node]:
            task = graph.nodes[node]["task"]
            if task in tasks:
                tasks[task].append(node)
            else:
                tasks[task] = [node]
    
    for edge in graph.edges():
        Edge_Start.append(int(edge[0]))
        Edge_End.append(int(edge[1])) 
        lenghts.append(int(graph.edges[edge]['length']))  

    # create binary representation of tasks
    task_binary = np.zeros((num_tasks, N), dtype=int)
    for i, task in enumerate(tasks):
        for node in tasks[task]:
            task_binary[i, int(node) - 1] = 1

    # Write the extracted information to text file for MIP solver
    filename3 = ".\\data\\mip\\tcsp\\" + filename + ".inst"
    with open(filename3, 'w') as f:
        f.write(f'{M} {N} {int(Start)-1} {int(End)-1} {num_tasks}\n')
        for edge in graph.edges():
            f.write(f'{int(edge[0])-1} {int(edge[1])-1} {graph.edges[edge]["length"]}\n')
        for i, task in enumerate(tasks):
            f.write(f'{" ".join(tasks[task])}\n')

files = glob.glob(f".\graphs\\tcsp\\*.graphml")
files.sort(key=os.path.getmtime)
print(files)
# fname = "graphs/basic-graph.graphml"
parser = GraphMLParser()
print(files)
for fname in files:
    graph = nx.read_graphml(fname)
    name = fname.split("\\")[-1].split(".")[0]
    print(name)
    create_data_file_tcsp(graph, name)
   

