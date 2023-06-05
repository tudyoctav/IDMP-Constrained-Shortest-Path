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

def create_data_file_rcsp(graphml_obj, filename):
    # Extract necessary information from the graphml_obj
    N = len(graphml_obj.nodes())
    M = len(graphml_obj.edges())
    Edge_Start = []
    Edge_End = []
    L = []
    T = []
    Start = 1
    End = N
    Lower_Bound = []
    Upper_Bound = []
        
    for edge in graphml_obj.edges(data = True):
        Edge_Start.append(int(edge[0]))
        Edge_End.append(int(edge[1]))
        L.append(int(edge[2]['weight']))  
        T.append(int(edge[2]['time'])) 


    for node in graphml_obj.nodes(data = True):
        Lower_Bound.append(int(node[1]["lower_bound"]))  
        Upper_Bound.append(int(node[1]["upper_bound"]))
        if "start" in node[1]:
            Start = node[0]
        if "end" in node[1]:
            End = node[0]
            Time = node[1]['final_time'] + 1

    # Write the extracted information to the MiniZinc .dzn file
    filename1 = "./data/cp/rcsp/" + filename + ".dzn"
    with open(filename1, 'w') as f:
        f.write(f'N = {N};\n')
        f.write(f'M = {M};\n')
        f.write(f'Edge_Start = {Edge_Start};\n')
        f.write(f'Edge_End = {Edge_End};\n')
        f.write(f'L = {L};\n')
        f.write(f'T = {T};\n')
        f.write(f'Lower_Bound = {Lower_Bound};\n')
        f.write(f'Upper_Bound = {Upper_Bound};\n')
        f.write(f'Start = {Start};\n')
        f.write(f'End = {End};\n')
        f.write(f'Time = {Time};\n')

    # Write the extracted information to a .txt file for the SAT solver
    filename2 = "./data/sat/rcsp/" + filename + ".txt"
    with open(filename2, 'w') as f:
        f.write(f'N = {N};\n')
        f.write(f'M = {M};\n')
        f.write(f'Edge_Start = {Edge_Start};\n')
        f.write(f'Edge_End = {Edge_End};\n')
        f.write(f'L = {L};\n')
        f.write(f'T = {T};\n')
        f.write(f'Lower_Bound = {Lower_Bound};\n')
        f.write(f'Upper_Bound = {Upper_Bound};\n')
        f.write(f'Start = {Start};\n')
        f.write(f'End = {End};\n')
        f.write(f'Time = {Time};\n')

    # Write the extracted information to a .txt file for the MIP solver
    filename3 = "./data/mip/rcsp/" + filename + ".txt"
    with open(filename3, 'w') as f:
        f.write(f'{M} {N} {Start} {End}')
        for edge in graphml_obj.edges(data = True):
            f.write(f'{edge[0]} {edge[1]} {edge[2]["weight"]} {edge[2]["time"]}')
        for node in graphml_obj.nodes(data = True):
            f.write(f'{node[1]["lower_bound"]} {node[1]["upper_bound"]}')

def create_data_file_tcsp(graphml_obj, filename):
    # Extract necessary information from the graphml_obj
    N = len(graphml_obj.nodes())
    M = len(graphml_obj.edges())
    Start = None
    End = None
    tasks = {}
    num_tasks = 0
    Edge_Start = []
    Edge_End = []
    weights = []
    for node in graphml_obj.nodes():
        if "start" in graphml_obj.nodes[node]:
            Start = node
        if "end" in graphml_obj.nodes[node]:
            End = node
        if "task" in graphml_obj.nodes[node]:
            task = graphml_obj.nodes[node]["task"]
            if task in tasks:
                tasks[task].append(node)
            else:
                tasks[task] = [node]
                num_tasks += 1
    
    for edge in graphml_obj.edges():
        Edge_Start.append(int(edge[0]))
        Edge_End.append(int(edge[1])) 
        weights.append(int(graphml_obj.edges[edge]['weight']))  

    # create binary representation of tasks
    task_binary = np.zeros((num_tasks, N), dtype=int)
    for i, task in enumerate(tasks):
        for node in tasks[task]:
            task_binary[i, int(node) - 1] = 1

    # Write the extracted information to the MiniZinc .dzn file
    filename1 = "./data/cp/tcsp/" + filename + ".dzn"
    with open(filename1, 'w') as f:
        f.write(f'nodes = {N};\n')
        f.write(f'edges = {M};\n')
        f.write(f'starts = {Edge_Start};\n')
        f.write(f'ends = {Edge_End};\n')
        f.write(f'weights = {weights};\n')
        f.write(f'start = {Start};\n')
        f.write(f'end= {End};\n')
        f.write(f'tasks = {num_tasks};\n')
        f.write(f'task = array2d(1..tasks, 1..nodes, {task_binary.flatten().tolist()});\n')

    # Write the extracted information to text file for SAT solver
    filename2 = "./data/sat/tcsp/" + filename + ".txt"
    with open(filename2, 'w') as f:
        f.write(f'{N} {M} {Start} {End} {num_tasks}\n')
        for edge in graphml_obj.edges():
            f.write(f'{edge[0]} {edge[1]} {graphml_obj.edges[edge]["weight"]}\n')
        for i, task in enumerate(tasks):
            f.write(f'{" ".join(tasks[task])}\n')

    # Write the extracted information to text file for MIP solver
    filename3 = "./data/mip/tcsp/" + filename + ".txt"
    with open(filename3, 'w') as f:
        f.write(f'{M} {N} {Start} {End} {num_tasks}\n')
        for edge in graphml_obj.edges():
            f.write(f'{edge[0]} {edge[1]} {graphml_obj.edges[edge]["weight"]}\n')
        for i, task in enumerate(tasks):
            f.write(f'{" ".join(tasks[task])}\n')


def get_source_target(graph):
    source = None
    target = None
    for node in graph.nodes():
        if "start" in graph.nodes[node]:
            source = node
        elif "end" in graph.nodes[node]:
            target = node
    return source, target

def add_time_attribute(graph):
    for u, v, attr in graph.edges.data():
        weight = attr.get('weight', 10)
        # Sample time attribute around the weight
        time = max(1,random.uniform(weight - 5, weight + 5))
        attr['time'] = time
    return graph


def add_time_constraint(graph):
    path = nx.shortest_path(graph, source, target, weight='time')

def display_graph(graph):
    pos = nx.spring_layout(graph)  # Compute the layout of the graph
    nx.draw(graph, pos, with_labels=True)  # Draw the graph with labels
    plt.show()  # Show the graph

def pick_random_tasks_for_twcsp(graph, considered_nodes):
    graph = graph.copy()
    if len(considered_nodes) < 2:
        num_tasks = len(considered_nodes)
    else:
        num_tasks = random.randint(1, len(considered_nodes))
    num_of_nodes_per_task = random.randint(1, len(considered_nodes) // num_tasks)
    select_subset = random.sample(considered_nodes ,num_tasks * num_of_nodes_per_task)
    select_subset = np.resize(select_subset, (num_tasks, num_of_nodes_per_task))
    # print(f"Generating {num_tasks} task(s) with {num_of_nodes_per_task} nodes per task: {[('task' + str(ind), val) for ind,val in enumerate(select_subset)]}")
    for task, nodes in enumerate(select_subset):
        for node in nodes:
            graph.nodes[node]["task"] = task
    return graph

def tcsp_along_shortest_path(graph, source, target):
    shortest_path = nx.shortest_path(graph, source, target, weight='weight')
    path_ids = [node for node in shortest_path]
    print("Shortest Path:", " -> ".join(str(node) for node in path_ids))
    print("Picking tasks along the shortest path...")
    return pick_random_tasks_for_twcsp(graph, path_ids) # pick nodes along the path

def tcsp_outside_shortes_path(graph, source, target):
    shortest_path = nx.shortest_path(graph, source, target, weight='weight')
    path_ids = [node for node in shortest_path]
    num_tasks = random.randint(2, len(path_ids))
    num_of_nodes_per_task = random.randint(1, len(path_ids) // num_tasks)
    considered_nodes = [node for node in graph.nodes() if node not in path_ids]
    print("Picking tasks outside the shortest path...")
    return pick_random_tasks_for_twcsp(graph, considered_nodes) # pick nodes outside the path

def twcsp_random(graph, source, target):
    print("Picking tasks randomly...")
    return pick_random_tasks_for_twcsp(graph, list(graph.nodes()))

def generate_constraints_for_tcsp(graph, source, target, name):
    graph_1 = tcsp_along_shortest_path(graph, source, target)
    name_1 = name + "_task_along_shortest_path"
    nx.write_graphml(graph_1, f"./graphs/tcsp/{name_1}.graphml", named_key_ids=True)
    create_data_file_tcsp(graph_1, name_1)   

    graph_2 = tcsp_outside_shortes_path(graph, source, target)
    name_2 = name + "_task_outside_shortest_path"
    nx.write_graphml(graph_2, f"./graphs/tcsp/{name_2}.graphml", named_key_ids=True)
    create_data_file_tcsp(graph_2, name_2)

    graph_3 = twcsp_random(graph, source, target)
    name_3 = name + "_task_random"
    nx.write_graphml(graph_3, f"./graphs/tcsp/{name_3}.graphml", named_key_ids=True)
    create_data_file_tcsp(graph_3, name_3)


def get_colour(time):
    if time < 2:
        colour = 'lightgreen'
    elif time < 3 :
        colour = 'green'
    elif time < 4 :
        colour = 'darkgreen'
    elif time < 5 :
        colour = 'yellow'
    elif time < 6 :
        colour = 'orange'
    elif time < 7 :
        colour = 'darkred'
    else:
        colour = 'red'
    return colour

def add_time_attributes(graph , pos = None, scale = 1, var = 5):
    graph = graph.copy()
    for (u, v) in graph.edges():
        distance = graph[u][v]['weight'] 
        graph[u][v]['time'] = max(1,int(np.random.normal(distance * scale, var)))
    return graph

def rcsp_all_nodes_are_reachable(graph, source, target):
    graph = graph.copy()
    # shortest_path = nx.shortest_path(graph, source, target, weight='time')
    time_shortes_paths = nx.single_source_dijkstra_path(graph, source, weight='time')
    time_shortest_lengts = nx.single_source_dijkstra_path_length(graph, source, weight='time')
    for n in graph.nodes():
        graph.nodes[n]['lower_bound'] = time_shortest_lengts[n]
        graph.nodes[n]['upper_bound'] = time_shortest_lengts[n] + 1
        if "end" in graph.nodes[n]: # if node is final node
            graph.nodes[n]['final_time'] = time_shortest_lengts[n] + 1 # also add the time for rcsp
    return graph

def generate_constraints_for_rcsp(graph, source, target, name):
    graph_time = add_time_attributes(graph)
    graph_1 = rcsp_all_nodes_are_reachable(graph_time, source, target)
    name_1 = name + "_all_nodes_are_reachable"
    nx.write_graphml(graph_1, f"./graphs/rcsp/{name_1}.graphml", named_key_ids=True)
    create_data_file_rcsp(graph_1, name_1)


files = glob.glob(f".\graphs\input\*.graphml")
# fname = "graphs/basic-graph.graphml"
parser = GraphMLParser()
for fname in files:
    graph = nx.read_graphml(fname)
    
    name = fname.split("\\")[-1].split(".")[0]
    print(name)
    source, target = get_source_target(graph)
    generate_constraints_for_tcsp(graph, source, target, name)       
    generate_constraints_for_rcsp(graph, source, target, name)
    display_graph(graph)