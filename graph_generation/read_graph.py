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

def create_data_file_rcsp(graph, filename):
    # Extract necessary information from the graphml_obj
    N = len(graph.nodes())
    M = len(graph.edges())
    Edge_Start = []
    Edge_End = []
    L = []
    T = []
    Start = graph.graph['start_node']
    End = graph.graph['finish_node']
    Time = graph.nodes(data=True)[End]['upper_bound']
    Lower_Bound = []
    Upper_Bound = []
    for edge in graph.edges(data = True):
        Edge_Start.append(int(edge[0]))
        Edge_End.append(int(edge[1]))
        L.append(int(edge[2]['length']))  
        T.append(int(edge[2]['travel_time'])) 

    for node in graph.nodes(data = True):
        Lower_Bound.append(int(node[1]["lower_bound"]))  
        Upper_Bound.append(int(node[1]["upper_bound"]))
            

    # Write the extracted information to the MiniZinc .dzn file
    filename1 = "./data/cp/rcsp/" + filename + ".dzn"
    with open(filename1, 'w') as f:
        f.write(f'N = {N};\n')
        f.write(f'M = {M * 2};\n')
        f.write(f'Edge_Start = {Edge_Start + Edge_End};\n') # double the edges since undirected
        f.write(f'Edge_End = {Edge_End + Edge_Start};\n') # write the reverse of the edges
        f.write(f'L = {L + L};\n') # double the edges since undirected
        f.write(f'T = {T + T};\n') # write the reverse of the edges
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
    filename3 = "./data/mip/rcsp/" + filename + ".inst"
    with open(filename3, 'w') as f:
        f.write(f'{M * 2} {N} {int(Start)-1} {int(End)-1}\n')
        for edge in graph.edges(data = True):
            f.write(f'{int(edge[0])-1} {int(edge[1])-1} {edge[2]["length"]} {edge[2]["length"]}\n')
            f.write(f'{int(edge[1])-1} {int(edge[0])-1} {edge[2]["length"]} {edge[2]["length"]}\n') # write the reverse of the edges since undirected
        for node in graph.nodes(data = True):
            f.write(f'{node[1]["lower_bound"]} {node[1]["upper_bound"]}\n')

def create_data_file_tcsp(graph, filename):
    # Extract necessary information from the graphml_obj
    N = len(graph.nodes())
    M = len(graph.edges())
    Start = graph.graph['start_node']
    End = graph.graph['finish_node']
    tasks = {}
    num_tasks = 0
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
                num_tasks += 1
    
    for edge in graph.edges():
        Edge_Start.append(int(edge[0]))
        Edge_End.append(int(edge[1])) 
        lenghts.append(int(graph.edges[edge]['length']))  

    # create binary representation of tasks
    task_binary = np.zeros((num_tasks, N), dtype=int)
    for i, task in enumerate(tasks):
        for node in tasks[task]:
            task_binary[i, int(node) - 1] = 1

    # Write the extracted information to the MiniZinc .dzn file
    filename1 = "./data/cp/tcsp/" + filename + ".dzn"
    with open(filename1, 'w') as f:
        f.write(f'nodes = {N};\n')
        f.write(f'edges = {M * 2};\n')
        f.write(f'starts = {Edge_Start + Edge_End};\n') # double the edges since undirected
        f.write(f'ends = {Edge_End + Edge_Start};\n') # write the reverse of the edges
        f.write(f'weights = {lenghts + lenghts};\n') # double the weights since undirected
        f.write(f'start = {Start};\n')
        f.write(f'end= {End};\n')
        f.write(f'tasks = {num_tasks};\n')
        f.write(f'task = array2d(1..tasks, 1..nodes, {task_binary.flatten().tolist()});\n')
    # Write the extracted information to text file for SAT solver
    filename2 = "./data/sat/tcsp/" + filename + ".txt"
    with open(filename2, 'w') as f:
        f.write(f'{N} {M} {Start} {End} {num_tasks}\n')
        for edge in graph.edges():
            f.write(f'{edge[0]} {edge[1]} {graph.edges[edge]["length"]}\n')
        for i, task in enumerate(tasks):
            f.write(f'{" ".join(tasks[task])}\n')

    # Write the extracted information to text file for MIP solver
    filename3 = "./data/mip/tcsp/" + filename + ".inst"
    with open(filename3, 'w') as f:
        f.write(f'{M * 2} {N} {int(Start)-1} {int(End)-1} {num_tasks}\n')
        for edge in graph.edges():
            f.write(f'{int(edge[0])-1} {int(edge[1])-1} {graph.edges[edge]["length"]}\n')
            f.write(f'{int(edge[1])-1} {int(edge[0])-1} {graph.edges[edge]["length"]}\n') # write the reverse of the edges since undirected
        for i, task in enumerate(tasks):
            f.write(f'{" ".join(tasks[task])}\n')


def relable_nodes(graph, custom = None):
    graph = graph.copy()
    mapping = {}
    ind = 1
    custom = custom if custom else range(len(graph.nodes()) + 1)
    for node in graph.nodes():
        mapping[node] = str(custom[ind])
        ind += 1
    nx.relabel_nodes(graph, mapping, copy = False)
    graph.graph['start_node'] = mapping[str(graph.graph['start_node'])]
    graph.graph['finish_node'] = mapping[str(graph.graph['finish_node'])]
    return graph, mapping

def display_graph_for_tcsp(graph, source, target,fig = None, draw_labels = False):
    init_pos = {node : (float(data['x']), float(data['y'])) for node,data in graph.nodes(data = True)}
    fig = fig if fig else plt.figure(figsize=(12,12))

    shortest_path_weight = nx.shortest_path(graph, source = source, target = target, weight = 'legnth')
    shortest_weight = nx.shortest_path_length(graph, source = source, target = target, weight = 'length')
    edges_in_shortest_path = [(str(min(int(u),int(v))), str(max(int(u),int(v)))) for (u,v) in zip(shortest_path_weight, shortest_path_weight[1:])]
    node_color = ["red" if n in shortest_path_weight else "tab:blue" for n in graph.nodes()]
    nx.draw_networkx(graph, pos=init_pos, with_labels=True ,node_color = node_color)
    num_nodes = len(graph.nodes())
    shift_pos = { 6 : 0.1, 16: 0.15, 30: 0.2,48: 0.2, 70 : 0.3, 96: 0.4}
    if draw_labels:
        length = nx.get_edge_attributes(graph,'length')
        labels = {edge : f"{length[edge]}" for edge in graph.edges()}
        if num_nodes in shift_pos:
            nx.draw_networkx_edge_labels(graph,pos = init_pos, edge_labels = labels, font_size = 10)

        if num_nodes in shift_pos:
            shift = shift_pos[num_nodes]
        else:
            shift = 0.4
        shifted_pos ={node: (node_pos[0],node_pos[1] - shift) for node, node_pos in init_pos.items()}
        node_labels = {node: str([data["task"] + 1]) if "task" in data else "" for node,data in graph.nodes(data = True)}
        # nx.draw_networkx_labels(G, shifted_pos, labels=node_labels, horizontalalignment="left", font_color = start_colour)
        nx.draw_networkx_labels(graph, shifted_pos, labels=node_labels)

def pick_random_tasks_for_tcsp(graph, source, target, considered_nodes):
    graph = graph.copy()
    norm = 5
    if len(considered_nodes) < 2:
        num_tasks = random.int(0,len(considered_nodes))
    else:
        num_tasks = random.randint(1, max(1,len(considered_nodes)//norm))
    num_of_nodes_per_task = random.randint(1, max(1,len(considered_nodes) // num_tasks // norm))
    select_subset = random.sample(considered_nodes ,num_tasks * num_of_nodes_per_task)
    select_subset = np.resize(select_subset, (num_tasks, num_of_nodes_per_task))
    # print(f"Generating {num_tasks} task(s) with {num_of_nodes_per_task} nodes per task: {[('task' + str(ind), val) for ind,val in enumerate(select_subset)]}")
    for task, nodes in enumerate(select_subset):
        for node in nodes:
            graph.nodes[node]["task"] = task
        
    graph.nodes[source]["num_tasks"] = num_tasks
    graph.nodes[source]["num_of_nodes_per_task"] = num_of_nodes_per_task
    return graph, num_tasks, num_of_nodes_per_task

def tcsp_along_shortest_path(graph, source, target):
    shortest_path = nx.shortest_path(graph, source, target, weight='weight')
    path_ids = [node for node in shortest_path]
    print("Shortest Path:", " -> ".join(str(node) for node in path_ids))
    print("Picking tasks along the shortest path...")
    return pick_random_tasks_for_tcsp(graph, source, target, path_ids) # pick nodes along the path

def tcsp_outside_shortes_path(graph, source, target):
    shortest_path = nx.shortest_path(graph, source, target, weight='weight')
    path_ids = [node for node in shortest_path]
    num_tasks = random.randint(2, len(path_ids))
    num_of_nodes_per_task = random.randint(1, len(path_ids) // num_tasks)
    considered_nodes = [node for node in graph.nodes() if node not in path_ids]
    print("Picking tasks outside the shortest path...")
    return pick_random_tasks_for_tcsp(graph, source, target, considered_nodes) # pick nodes outside the path

def tcsp_random(graph, source, target):
    print("Picking tasks randomly...")
    return pick_random_tasks_for_tcsp(graph, source, target, list(graph.nodes()))

def generate_constraints_for_tcsp(graph, source, target, name):
    
    graph_1, num_tasks, num_nodes_per_task = tcsp_along_shortest_path(graph, source, target)
    name_1 = name + "_task_along_shortest_path"
    nx.write_graphml(graph_1, f"./graphs/tcsp/{name_1}.graphml", named_key_ids=True)
    create_data_file_tcsp(graph_1, name_1)   
    display_graph_for_tcsp(graph_1, source, target, draw_labels = True)
    plt.title(f"Task along shortest path with #tasks = {num_tasks}, #nodes_per_task = {num_nodes_per_task}")
    plt.savefig(f"./images/tcsp/{name_1}.png")


    
    graph_2, num_tasks, num_nodes_per_task = tcsp_outside_shortes_path(graph, source, target)
    name_2 = name + "_task_outside_shortest_path"
    nx.write_graphml(graph_2, f"./graphs/tcsp/{name_2}.graphml", named_key_ids=True)
    create_data_file_tcsp(graph_2, name_2)
    display_graph_for_tcsp(graph_2, source, target, draw_labels = True)
    plt.title(f"Task outside shortest path with #tasks = {num_tasks}, #nodes_per_task = {num_nodes_per_task}")
    plt.savefig(f"./images/tcsp/{name_2}.png")
 
    graph_3, num_tasks, num_nodes_per_task = tcsp_random(graph, source, target)
    name_3 = name + "_task_random"
    nx.write_graphml(graph_3, f"./graphs/tcsp/{name_3}.graphml", named_key_ids=True)
    create_data_file_tcsp(graph_3, name_3)
    display_graph_for_tcsp(graph_3, source, target, draw_labels = True)
    plt.title(f"Task random with #tasks = {num_tasks}, #nodes_per_task = {num_nodes_per_task}")
    plt.savefig(f"./images/tcsp/{name_3}.png")

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


# def add_time_attribute(graph):
#     for u, v, attr in graph.edges.data():
#         weight = attr.get('weight', 10)
#         # Sample time attribute around the weight
#         time = max(1,random.uniform(weight - 5, weight + 5))
#         attr['time'] = time
#     print("BRAAAAAAAAAAAAAAAAA")
#     return graph

def add_weights(graph , pos = None, scale = 1, var = 5):
    graph = graph.copy()
    for (u, v) in graph.edges():
        if 'travel_time' not in graph[u][v]:
            distance = graph[u][v]['length']
            graph[u][v]['travel_time'] = max(1,int(np.random.normal(distance * scale, var)))
        if 'length' not in graph[u][v]:
            TimeoutError = graph[u][v]['travel_time']
            graph[u][v]['length'] = max(1,int(np.random.normal(time / scale, var)))
    return graph


def rcsp_all_nodes_are_reachable(graph, source, target):
    graph = graph.copy()
    # shortest_path = nx.shortest_path(graph, source, target, weight='time')
    time_shortes_paths = nx.single_source_dijkstra_path(graph, source, weight='travel_time')
    time_shortest_lengts = nx.single_source_dijkstra_path_length(graph, source, weight='travel_time')
    for n in graph.nodes():
        graph.nodes[n]['lower_bound'] = time_shortest_lengts[n]
        graph.nodes[n]['upper_bound'] = time_shortest_lengts[n]
    return graph

def generate_constraints_for_rcsp(graph, source, target, name):
    graph_time = add_weights(graph)
    graph_1 = rcsp_all_nodes_are_reachable(graph_time, source, target)
    name_1 = name + "_all_nodes_are_reachable"
    nx.write_graphml(graph_1, f"./graphs/rcsp/{name_1}.graphml", named_key_ids=True)
    create_data_file_rcsp(graph_1, name_1)
    display_graph_for_rcsp(graph_1, source, target, draw_labels = True)
    plt.title("All nodes are reachable")
    plt.savefig(f"./images/rcsp/{name_1}.png")

def make_weights_int(graph):
    graph = graph.copy()
    for (u, v) in graph.edges():
        if 'length' in graph[u][v]:
            graph[u][v]['length'] = int(float(graph[u][v]['length']))
        if 'travel_time' in graph[u][v]:
            graph[u][v]['travel_time'] = int(float(graph[u][v]['travel_time']))
    return graph

def display_graph_for_rcsp(graph, source, target,fig = None, draw_labels = False):
    init_pos = {node : (float(data['x']), float(data['y'])) for node,data in graph.nodes(data = True)}
    fig = fig if fig else plt.figure(figsize=(10,10))


    shortest_path_length = nx.shortest_path(graph, source = source, target = target, weight = 'length')
    shortest_length = nx.shortest_path_length(graph, source = source, target = target, weight = 'length')
    shortest_path_time = nx.shortest_path(graph, source = source, target = target, weight = 'travel_time')
    shortest_time = nx.shortest_path_length(graph, source = source, target = target, weight = 'travel_time')
    edges_in_shortest_time_path = [(str(min(int(u),int(v))), str(max(int(u),int(v)))) for (u,v) in zip(shortest_path_time, shortest_path_time[1:])]
    print(f"Shortest length {shortest_length} with path: {shortest_path_length}")
    print(f"Shortest time {shortest_time} with path: {shortest_path_time}")
    print(f"Edges in shortest time path: {edges_in_shortest_time_path}")
    node_color = ["red" if n in shortest_path_length else "tab:blue" for n in graph.nodes()]

    edge_color = ["magenta" if ((u,v) or (v,u)) in edges_in_shortest_time_path else "tab:blue" for u,v in graph.edges()]
    nx.draw_networkx(graph, pos=init_pos, with_labels=True ,node_color = node_color, edge_color=edge_color)
    num_nodes = len(graph.nodes())
    shift_pos = { 6 : 0.1, 16: 0.15, 30: 0.2, 48: 0.2, 70 : 0.3}
    if draw_labels and num_nodes in shift_pos:
        weight = nx.get_edge_attributes(graph,'length')
        time = nx.get_edge_attributes(graph,'travel_time')
        labels = {edge : f"{weight[edge]} / {time[edge]}" for edge in graph.edges()}
        nx.draw_networkx_edge_labels(graph,pos = init_pos, edge_labels = labels, font_size = 10)
       
        if num_nodes in shift_pos:
            shift = shift_pos[num_nodes]
        else:
            shift = 0.4
        shifted_pos ={node: (node_pos[0],node_pos[1] - shift) for node, node_pos in init_pos.items()}
        node_labels = {node: (data['lower_bound'], data['upper_bound']) for node,data in graph.nodes(data = True)}
        # nx.draw_networkx_labels(G, shifted_pos, labels=node_labels, horizontalalignment="left", font_color = start_colour)
        nx.draw_networkx_labels(graph, shifted_pos, labels=node_labels)

folder = ".\graphs\input\\"
# folder = ".\cities\output-subsamples\\"

files = glob.glob(f"{folder}*.graphml")
files.sort(key=os.path.getmtime)
parser = GraphMLParser()
for fname in files:
    graph = nx.read_graphml(fname)
    name = fname.split("\\")[-1].split(".")[0]
    print(f"----------------------------------------------------\nProcessing {name}...")

    graph = make_weights_int(graph)
    graph, mapping = relable_nodes(graph)
    source = graph.graph["start_node"]
    target = graph.graph["finish_node"]

   
    graph = make_weights_int(graph)
    generate_constraints_for_tcsp(graph, source, target, name)       
    generate_constraints_for_rcsp(graph, source, target, name)
    plt.show(block=False)
    plt.pause(0.1)
    plt.close()
