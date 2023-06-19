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

def create_data_file_sp(graph, filename):
    # double the edges to make graph directed
    if not nx.is_directed(graph):
        graph = graph.to_directed()
    # Extract necessary information from the graphml_obj
    N = len(graph.nodes())
    M = len(graph.edges())
    Edge_Start = []
    Edge_End = []
    L = []
    Start = graph.graph['start_node']
    End = graph.graph['finish_node']
    for edge in graph.edges(data = True):
        Edge_Start.append(int(edge[0]))
        Edge_End.append(int(edge[1]))
        L.append(int(edge[2]['length']))
    # Write the extracted information to the MiniZinc .dzn file
    filename1 = "./data/cp/sp/" + filename + ".dzn"
    with open(filename1, 'w') as f:
        f.write(f'N = {N};\n')
        f.write(f'M = {M};\n')
        f.write(f'Edge_Start = {Edge_Start};\n')
        f.write(f'Edge_End = {Edge_End};\n')
        f.write(f'L = {L};\n')
        f.write(f'Start = {Start};\n')
        f.write(f'End = {End};\n')

    # Write the extracted information to a .txt file for the SAT solver
    filename2 = "./data/sat/sp/" + filename + ".txt"
    with open(filename2, 'w') as f:
        f.write(f'N = {N};\n')
        f.write(f'M = {M};\n')
        f.write(f'Edge_Start = {Edge_Start};\n')
        f.write(f'Edge_End = {Edge_End};\n')
        f.write(f'L = {L};\n')
        f.write(f'Start = {Start};\n')
        f.write(f'End = {End};\n')

    # Write the extracted information to a .txt file for the MIP solver
    filename3 = "./data/mip/sp/" + filename + ".inst"
    with open(filename3, 'w') as f:
        f.write(f'{M} {N} {int(Start)-1} {int(End)-1}\n')
        for edge in graph.edges(data = True):
            f.write(f'{int(edge[0])-1} {int(edge[1])-1} {edge[2]["length"]}\n')

def create_data_file_rcsp(graph, filename):
    if not nx.is_directed(graph):
        graph = graph.to_directed()
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
        f.write(f'M = {M};\n')
        f.write(f'Edge_Start = {Edge_Start};\n') # double the edges since undirected
        f.write(f'Edge_End = {Edge_End};\n') # write the reverse of the edges
        f.write(f'L = {L};\n') # double the edges since undirected
        f.write(f'T = {T};\n') # write the reverse of the edges
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
        f.write(f'{M} {N} {int(Start)-1} {int(End)-1}\n')
        for edge in graph.edges(data = True):
            f.write(f'{int(edge[0])-1} {int(edge[1])-1} {edge[2]["length"]} {edge[2]["travel_time"]}\n')
        for node in graph.nodes(data = True):
            f.write(f'{node[1]["lower_bound"]} {node[1]["upper_bound"]}\n')

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

    # Write the extracted information to the MiniZinc .dzn file
    filename1 = "./data/cp/tcsp/" + filename + ".dzn"
    with open(filename1, 'w') as f:
        f.write(f'nodes = {N};\n')
        f.write(f'edges = {M};\n')
        f.write(f'starts = {Edge_Start};\n') # double the edges since undirected
        f.write(f'ends = {Edge_End};\n') # write the reverse of the edges
        f.write(f'weights = {lenghts};\n') # double the weights since undirected
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
        f.write(f'{M} {N} {int(Start)-1} {int(End)-1} {num_tasks}\n')
        for edge in graph.edges():
            f.write(f'{int(edge[0])-1} {int(edge[1])-1} {graph.edges[edge]["length"]}\n')
        for i, task in enumerate(tasks):
            f.write(f'{" ".join(tasks[task])}\n')

def create_data_file_ncsp(graph, filename):
    if not nx.is_directed(graph):
        graph = graph.to_directed()
    assert graph.graph["type"] == "ncsp"
    N = len(graph.nodes())
    M = len(graph.edges())
    Start = graph.graph['start_node']
    End = graph.graph['finish_node']
    num_tasks = graph.graph["num_nodes"]
    Edge_Start = []
    Edge_End = []
    penalties = []
    tasks = {}
    lenghts = []
    for node in graph.nodes():
        if "penalty" in graph.nodes[node]:
            penalties.append(int(graph.nodes[node]["penalty"]))
            tasks[node] = graph.nodes[node]["penalty"]
        else:
            penalties.append(0)
    
    for edge in graph.edges():
        Edge_Start.append(int(edge[0]))
        Edge_End.append(int(edge[1])) 
        lenghts.append(int(graph.edges[edge]['length']))  

    # Write the extracted information to the MiniZinc .dzn file
    filename1 = "./data/cp/ncsp/" + filename + ".dzn"
    with open(filename1, 'w') as f:
        f.write(f'nodes = {N};\n')
        f.write(f'edges = {M};\n')
        f.write(f'starts = {Edge_Start};\n') # double the edges since undirected
        f.write(f'ends = {Edge_End};\n') # write the reverse of the edges
        f.write(f'weights = {lenghts};\n') # double the weights since undirected
        f.write(f'start = {Start};\n')
        f.write(f'end= {End};\n')
        # f.write(f'tasks = {num_tasks};\n')
        f.write(f'p = {penalties};\n')
    # Write the extracted information to text file for SAT solver
    filename2 = "./data/sat/ncsp/" + filename + ".txt"
    with open(filename2, 'w') as f:
        f.write(f'{N} {M} {Start} {End} {num_tasks}\n')
        for edge in graph.edges():
            f.write(f'{edge[0]} {edge[1]} {graph.edges[edge]["length"]}\n')
        for n, p in tasks.items():
            f.write(f"{n} {p}\n")

    # Write the extracted information to text file for MIP solver
    filename3 = "./data/mip/ncsp/" + filename + ".inst"
    with open(filename3, 'w') as f:
        f.write(f'{M} {N} {int(Start)-1} {int(End)-1} {num_tasks}\n')
        for edge in graph.edges():
            f.write(f'{int(edge[0])-1} {int(edge[1])-1} {graph.edges[edge]["length"]}\n')
        for n, p in tasks.items():
            f.write(f"{int(n)-1} {p}\n")

def pick_random_tasks_for_tcsp(graph, source, target, considered_nodes, num_tasks, num_of_nodes_per_task):
    print(f"Generating {num_tasks} task(s) with {num_of_nodes_per_task} nodes per task")
    select_subset = random.sample(considered_nodes ,num_tasks * num_of_nodes_per_task)
    select_subset = np.resize(select_subset, (num_tasks, num_of_nodes_per_task))
    for task, nodes in enumerate(select_subset):
        for node in nodes:
            graph.nodes[node]["task"] = task
    
    graph.graph["num_tasks"] = num_tasks
    graph.graph["num_of_nodes_per_task"] = num_of_nodes_per_task
    return graph

def tcsp_along_shortest_path(graph, source, target, num_tasks, num_of_nodes_per_task):
    graph = graph.copy()
    shortest_path = nx.shortest_path(graph, source = source, target = target, weight='length')
    path_ids = [node for node in shortest_path]
    return pick_random_tasks_for_tcsp(graph, source, target, path_ids, num_tasks, num_of_nodes_per_task)

def tcsp_outside_shortes_path(graph, source, target, num_tasks, num_of_nodes_per_task, select_subset):
    graph = graph.copy()
    # print(f"Generating {num_tasks} task(s) with {num_of_nodes_per_task} nodes per task: {[('task' + str(ind), val) for ind,val in enumerate(select_subset)]}")
    for task, nodes in enumerate(select_subset):
        for node in nodes:
            graph.nodes[node]["task"] = task
        
    graph.graph["num_tasks"] = num_tasks
    graph.graph["num_of_nodes_per_task"] = num_of_nodes_per_task
    return graph

def rcsp_add_tight_bounds(graph, source, target):
    graph = graph.copy()
    # shortest_path = nx.shortest_path(graph, source, target, weight='time')
    time_shortest_paths = nx.single_source_dijkstra_path(graph, source, weight='travel_time')
    time_shortest_lengts = nx.single_source_dijkstra_path_length(graph, source, weight='travel_time')
    for n in graph.nodes():
        graph.nodes[n]['lower_bound'] = time_shortest_lengts[n]
        graph.nodes[n]['upper_bound'] = time_shortest_lengts[n]
    return graph

def rcsp_add_loose_bounds(graph, source, target):
    graph = graph.copy()
    # shortest_path = nx.shortest_path(graph, source, target, weight='time')
    time_shortest_paths = nx.single_source_dijkstra_path(graph, source, weight='travel_time')
    time_shortest_lengts = nx.single_source_dijkstra_path_length(graph, source, weight='travel_time')

    for n in graph.nodes():
        interval = np.random.geometric(0.2) 
        var = np.random.geometric(0.7) - 1
        graph.nodes[n]['lower_bound'] = var + time_shortest_lengts[n]
        graph.nodes[n]['upper_bound'] = var + time_shortest_lengts[n] + interval
    return graph

def add_weights_random(graph , scale = 1, var = 5):
    flag = True
    iter = 0
    while flag and iter < 100:
        result = graph.copy()
        for (u, v) in result.edges():
            if 'travel_time' not in result[u][v]:
                distance = result[u][v]['length']
                result[u][v]['travel_time'] = max(1,int(np.random.normal(distance * scale, var)))
            if 'length' not in result[u][v]:
                time = result[u][v]['travel_time']
                result[u][v]['length'] = max(1,int(np.random.normal(time / scale, var)))
       
        shortest_path_length = nx.shortest_path(result, source = source, target = target, weight = 'length')
        shortest_length = nx.shortest_path_length(result, source = source, target = target, weight = 'length')
        shortest_path_time = nx.shortest_path(result, source = source, target = target, weight = 'travel_time')
        shortest_time = nx.shortest_path_length(result, source = source, target = target, weight = 'travel_time')
        flag = (shortest_path_length == shortest_path_time)
        # print(f"Shortest length {shortest_length} = {shortest_path_length}")
        # print(f"Shortest time {shortest_time} = {shortest_path_time}")
        iter += 1
    return result

def add_weights_all_one(graph):
    graph = graph.copy()
    for (u, v) in graph.edges():
        graph[u][v]['travel_time'] = 1
        graph[u][v]['length'] = 1
    return graph

def ncsp_all_one(graph, source, target, num_nodes, selected_nodes):
    graph = graph.copy()
    graph.graph['num_nodes'] = num_nodes
    graph.graph['type'] = 'ncsp'
    for n in selected_nodes:
        graph.nodes[n]['penalty'] = 1
    return graph

def ncsp_all_random(graph, source, target, num_nodes, selected_nodes):
    graph = graph.copy()
    graph.graph['num_nodes'] = num_nodes
    graph.graph['type'] = 'ncsp'
    sum = 0
    for edge in graph.edges():
        sum += graph[edge[0]][edge[1]]['length']
    sum /= len(graph.edges())
    mean = sum * len(graph.nodes()) ** 0.5
    var = mean / 2
    for n in selected_nodes:
        graph.nodes[n]['penalty'] = max(1,int(np.random.normal(mean, var)))
    return graph

def generate_constraints_for_sp(graph, source, target, name):
    create_data_file_sp(graph, name)
    nx.write_graphml(graph, f"./graphs/sp/{name}.graphml", named_key_ids=True)
    display_graph_for_sp(graph, source, target, name)
    plt.savefig(f"./images/sp/{name}.png")

def generate_constraints_for_ncsp(graph, source, target, name):
    # pick the nodes
    mean_num_nodes = len(graph.nodes()) ** 0.5
    num_nodes = max(1,int(np.random.normal(mean_num_nodes, mean_num_nodes / 2)))
    nodes = list(graph.nodes())
    selected_nodes = np.random.shuffle(nodes)
    selected_nodes = nodes[:num_nodes]
    print(f"Selected nodes for NCSP {selected_nodes}")
    # all weights are equal to one
    graph_weights_one = add_weights_all_one(graph)
    graph_penalty_one_weights_one = ncsp_all_one(graph_weights_one, source, target, num_nodes, selected_nodes)
    graph_penalty_random_weights_one = ncsp_all_random(graph_weights_one, source, target, num_nodes, selected_nodes)
    name_penalty_one_weights_one = f"{name}_penalty-one_weights-one"
    name_penalty_random_weights_one = f"{name}_penalty-random_weights-one"
    nx.write_graphml(graph_penalty_one_weights_one, f"./graphs/ncsp/{name_penalty_one_weights_one}.graphml", named_key_ids=True)
    nx.write_graphml(graph_penalty_random_weights_one, f"./graphs/ncsp/{name_penalty_random_weights_one}.graphml", named_key_ids=True)
    create_data_file_ncsp(graph_penalty_one_weights_one, name_penalty_one_weights_one)
    create_data_file_ncsp(graph_penalty_random_weights_one, name_penalty_random_weights_one)

    # all weights are random
    graph_weights_random = add_weights_random(graph)
    graph_penalty_one_random_weights = ncsp_all_one(graph_weights_random, source, target, num_nodes, selected_nodes)
    graph_penalty_random_random_weights = ncsp_all_random(graph_weights_random, source, target, num_nodes, selected_nodes)
    name_penalty_one_random_weights = f"{name}_penalty-one_random-weights"
    name_penalty_random_random_weights = f"{name}_penalty-random-random_weights"
    nx.write_graphml(graph_penalty_one_random_weights, f"./graphs/ncsp/{name_penalty_one_random_weights}.graphml", named_key_ids=True)
    nx.write_graphml(graph_penalty_random_random_weights, f"./graphs/ncsp/{name_penalty_random_random_weights}.graphml", named_key_ids=True)
    create_data_file_ncsp(graph_penalty_one_random_weights, name_penalty_one_random_weights)
    create_data_file_ncsp(graph_penalty_random_random_weights, name_penalty_random_random_weights)

    display_graph_for_ncsp(graph_penalty_one_weights_one, source, target, title = "Weights are all one and penalty is one")
    plt.savefig(f"./images/ncsp/{name_penalty_one_weights_one}.png")
    display_graph_for_ncsp(graph_penalty_random_weights_one, source, target, title = "Weights are all one and penalty is random")
    plt.savefig(f"./images/ncsp/{name_penalty_random_weights_one}.png")
    display_graph_for_ncsp(graph_penalty_one_random_weights, source, target, title = "Weights are random and penalty is one")
    plt.savefig(f"./images/ncsp/{name_penalty_one_random_weights}.png")
    display_graph_for_ncsp(graph_penalty_random_random_weights, source, target, title = "Weights are random and penalty is random")
    plt.savefig(f"./images/ncsp/{name_penalty_random_random_weights}.png")
    plt.close('all')

def generate_constraints_for_tcsp(graph, source, target, name):
    try:
        # generated number of nodes
        if len(graph.nodes()) < 20:
            mean_num_nodes = 3
        elif len(graph.nodes()) < 50:
            mean_num_nodes = 5
        elif len(graph.nodes()) < 100:
            mean_num_nodes = 10
        else:
            mean_num_nodes = min(25,len(graph.nodes()) ** 0.5)
        print(mean_num_nodes)
        num_tasks =  max(2,int(random.uniform(1,mean_num_nodes)))
        mean_num_of_nodes_per_task = min(25,len(graph.nodes()) // num_tasks)
        print(mean_num_of_nodes_per_task)
        num_of_nodes_per_task = max(1,int(random.uniform(1,mean_num_nodes)))
        select_random = random.sample(graph.nodes() ,num_tasks * num_of_nodes_per_task)
        select_random = np.resize(select_random, (num_tasks, num_of_nodes_per_task))

        print(f"Number of tasks {num_tasks} and number of nodes per task {num_of_nodes_per_task}")
        # all weights are equal to one
        graph_weights_one = add_weights_all_one(graph)
        graph_inside_path_weights_one = tcsp_along_shortest_path(graph_weights_one, source, target, num_tasks, num_of_nodes_per_task)
        graph_outside_path_weights_one = tcsp_outside_shortes_path(graph_weights_one, source, target, num_tasks, num_of_nodes_per_task, select_random)
        # graph_random_weights_one = tcsp_random(graph_weights_one, source, target)
        name_inside_path_one = f"{name}_weights-one_inside-path"
        name_outside_path_one = f"{name}_weights-one_outside-path"
        nx.write_graphml(graph_inside_path_weights_one, f"./graphs/tcsp/{name_inside_path_one}.graphml", named_key_ids=True)
        nx.write_graphml(graph_outside_path_weights_one, f"./graphs/tcsp/{name_outside_path_one}.graphml", named_key_ids=True)
        create_data_file_tcsp(graph_inside_path_weights_one, name_inside_path_one)
        create_data_file_tcsp(graph_outside_path_weights_one, name_outside_path_one)

        # all weights are random
        graph_weights_random = add_weights_random(graph)
        graph_inside_path_weights_random = tcsp_along_shortest_path(graph_weights_random, source, target, num_tasks, num_of_nodes_per_task)
        graph_outside_path_weights_random = tcsp_outside_shortes_path(graph_weights_random, source, target, num_tasks, num_of_nodes_per_task, select_random)
        # graph_random_weights_random = tcsp_random(graph_weights_random, source, target)
        name_inside_path_random = f"{name}_weights-random_inside-path"
        name_outside_path_random = f"{name}_weights-random_outside-path"
        nx.write_graphml(graph_inside_path_weights_random, f"./graphs/tcsp/{name_inside_path_random}.graphml", named_key_ids=True)
        nx.write_graphml(graph_outside_path_weights_random, f"./graphs/tcsp/{name_outside_path_random}.graphml", named_key_ids=True)
        create_data_file_tcsp(graph_inside_path_weights_random, name_inside_path_random)
        create_data_file_tcsp(graph_outside_path_weights_random, name_outside_path_random)
        
        # display graphs
        display_graph_for_tcsp(graph_inside_path_weights_one, source, target, title = "Weights are all one and tasks are on the shortest path")
        plt.savefig(f"./images/tcsp/{name_inside_path_one}.png")
        display_graph_for_tcsp(graph_outside_path_weights_one, source, target, title = "Weights are all one and tasks are outside the shortest path")
        plt.savefig(f"./images/tcsp/{name_outside_path_one}.png")
        display_graph_for_tcsp(graph_inside_path_weights_random, source, target, title = "Weights are random and tasks are on the shortest path")
        plt.savefig(f"./images/tcsp/{name_inside_path_random}.png")
        display_graph_for_tcsp(graph_outside_path_weights_random, source, target, title = "Weights are random and tasks are outside the shortest path")
        plt.savefig(f"./images/tcsp/{name_outside_path_random}.png")
        plt.close('all')
    except:
        print("Error in generating constraints for tcsp")
        generate_constraints_for_tcsp(graph, source, target, name)

def generate_constraints_for_rcsp(graph, source, target, name):
    # all weights are equal to one
    graph_weights_one = add_weights_all_one(graph)
    graph_tight_one = rcsp_add_tight_bounds(graph_weights_one, source, target)
    graph_loose_one = rcsp_add_loose_bounds(graph_weights_one, source, target)
    name_tight_one = f"{name}_weights-one_windows-tight"
    name_loose_one = f"{name}_weights-one_windows-loose"
    nx.write_graphml(graph_tight_one, f"./graphs/rcsp/{name_tight_one}.graphml", named_key_ids=True)
    nx.write_graphml(graph_loose_one, f"./graphs/rcsp/{name_loose_one}.graphml", named_key_ids=True)
    create_data_file_rcsp(graph_tight_one, name_tight_one)
    create_data_file_rcsp(graph_loose_one, name_loose_one)

    # all weights are random
    graph_weights_random = add_weights_random(graph)
    graph_tight_random = rcsp_add_tight_bounds(graph_weights_random, source, target) 
    graph_loose_random = rcsp_add_loose_bounds(graph_weights_random, source, target) 
    name_tight_random = f"{name}_weights-random_windows-tight" 
    name_loose_random = f"{name}_weights-random_windows-loose"
    nx.write_graphml(graph_tight_random, f"./graphs/rcsp/{name_tight_random}.graphml", named_key_ids=True)
    nx.write_graphml(graph_loose_random, f"./graphs/rcsp/{name_loose_random}.graphml", named_key_ids=True)
    create_data_file_rcsp(graph_tight_random, name_tight_random)
    create_data_file_rcsp(graph_loose_random, name_loose_random)

    # display graphs
    display_graph_for_rcsp(graph_tight_one, source, target, title = "Weights are all one and windows are tight")
    plt.savefig(f"./images/rcsp/{name_tight_one}.png")
    display_graph_for_rcsp(graph_loose_one, source, target, title = "Weights are all one and windows are loose")
    plt.savefig(f"./images/rcsp/{name_loose_one}.png")
    display_graph_for_rcsp(graph_tight_random, source, target, title = "Weights are random and windows are tight")
    plt.savefig(f"./images/rcsp/{name_tight_random}.png")
    display_graph_for_rcsp(graph_loose_random, source, target, title = "Weights are random and windows are loose")
    plt.savefig(f"./images/rcsp/{name_loose_random}.png")
    plt.close('all')

def display_graph_for_sp(graph, source, target,fig = None, title = None):
    init_pos = {node : (float(data['x']), float(data['y'])) for node,data in graph.nodes(data = True)}
    fig = fig if fig else plt.figure(figsize=(12,12))
    if title:
        plt.title(title)
    shortest_path = nx.shortest_path(graph, source = source, target = target, weight = 'length')
    shortest_weight = nx.shortest_path_length(graph, source = source, target = target, weight = 'length')
    edges_in_shortest_path = [(str(min(int(u),int(v))), str(max(int(u),int(v)))) for (u,v) in zip(shortest_path, shortest_path[1:])]
    node_color = ["red" if n in shortest_path else "tab:blue" for n in graph.nodes()]
    num_nodes = len(graph.nodes())
    nx.draw_networkx(graph, pos=init_pos, with_labels= num_nodes < 300 ,node_color = node_color)
    shift_pos = { 6 : 0.1, 16: 0.15, 30: 0.2,48: 0.2, 70 : 0.3, 96: 0.4}
    if num_nodes < 900:
        length = nx.get_edge_attributes(graph,'length')
        labels = {edge : f"{length[edge]}" for edge in graph.edges()}
        if num_nodes in shift_pos:
            nx.draw_networkx_edge_labels(graph,pos = init_pos, edge_labels = labels, font_size = 10)

def display_graph_for_rcsp(graph, source, target,fig = None, title = None):
    init_pos = {node : (float(data['x']), float(data['y'])) for node,data in graph.nodes(data = True)}
    fig = fig if fig else plt.figure(figsize=(10,10))
    plt.title(title)
    num_nodes = len(graph.nodes())
    draw_labels = True
    if num_nodes > 70:
        draw_labels = False
    shortest_path_length = nx.shortest_path(graph, source = source, target = target, weight = 'length')
    shortest_length = nx.shortest_path_length(graph, source = source, target = target, weight = 'length')
    shortest_path_time = nx.shortest_path(graph, source = source, target = target, weight = 'travel_time')
    shortest_time = nx.shortest_path_length(graph, source = source, target = target, weight = 'travel_time')
    edges_in_shortest_time_path = [(str(min(int(u),int(v))), str(max(int(u),int(v)))) for (u,v) in zip(shortest_path_time, shortest_path_time[1:])]
    # print(f"Shortest length {shortest_length} with path: {shortest_path_length}")
    # print(f"Shortest time {shortest_time} with path: {shortest_path_time}")
    # print(f"Edges in shortest time path: {edges_in_shortest_time_path}")
    node_color = ["red" if n in shortest_path_length else "tab:blue" for n in graph.nodes()]
    edge_color = ["magenta" if ((u,v) or (v,u)) in edges_in_shortest_time_path else "tab:blue" for u,v in graph.edges()]
    nx.draw_networkx(graph, pos=init_pos, with_labels=draw_labels ,node_color = node_color, edge_color=edge_color)
    shift_pos = { 6 : 0.1, 16: 0.15, 30: 0.2, 48: 0.2, 70 : 0.3}
    font_size = { 6 : 10, 16: 9, 30: 8, 48: 7, 70 : 6 }
    if draw_labels and num_nodes in shift_pos:
        weight = nx.get_edge_attributes(graph,'length')
        time = nx.get_edge_attributes(graph,'travel_time')
        labels = {edge : f"{weight[edge]} / {time[edge]}" for edge in graph.edges()}
        nx.draw_networkx_edge_labels(graph,pos = init_pos, edge_labels = labels, font_size = font_size[num_nodes])
        if num_nodes in shift_pos:
            shift = shift_pos[num_nodes]
        else:
            shift = 0.4
        shifted_pos ={node: (node_pos[0],node_pos[1] - shift) for node, node_pos in init_pos.items()}
        node_labels = {node: (data['lower_bound'], data['upper_bound']) for node,data in graph.nodes(data = True)}
        # nx.draw_networkx_labels(G, shifted_pos, labels=node_labels, horizontalalignment="left", font_color = start_colour)
        nx.draw_networkx_labels(graph, shifted_pos, labels=node_labels, font_size= font_size[num_nodes])
   
def display_graph_for_tcsp(graph, source, target,fig = None, draw_labels = None, title = None):
    init_pos = {node : (float(data['x']), float(data['y'])) for node,data in graph.nodes(data = True)}
    fig = fig if fig else plt.figure(figsize=(12,12))
    if title:
        plt.title(title)
    shortest_path = nx.shortest_path(graph, source = source, target = target, weight = 'length')
    shortest_weight = nx.shortest_path_length(graph, source = source, target = target, weight = 'length')
    edges_in_shortest_path = [(str(min(int(u),int(v))), str(max(int(u),int(v)))) for (u,v) in zip(shortest_path, shortest_path[1:])]
    node_color = ["red" if n in shortest_path else "tab:blue" for n in graph.nodes()]
    nx.draw_networkx(graph, pos=init_pos, with_labels=True ,node_color = node_color)
    num_nodes = len(graph.nodes())
    shift_pos = { 6 : 0.1, 16: 0.15, 30: 0.2,48: 0.2, 70 : 0.3, 96: 0.4}
    if num_nodes < 900:
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

def display_graph_for_ncsp(graph, source, target,fig = None, draw_labels = None, title = None):
    init_pos = {node : (float(data['x']), float(data['y'])) for node,data in graph.nodes(data = True)}
    fig = fig if fig else plt.figure(figsize=(12,12))
    if title:
        plt.title(title)
    shortest_path = nx.shortest_path(graph, source = source, target = target, weight = 'length')
    shortest_weight = nx.shortest_path_length(graph, source = source, target = target, weight = 'length')
    edges_in_shortest_path = [(str(min(int(u),int(v))), str(max(int(u),int(v)))) for (u,v) in zip(shortest_path, shortest_path[1:])]
    node_color = ["red" if n in shortest_path else "tab:blue" for n in graph.nodes()]
    nx.draw_networkx(graph, pos=init_pos, with_labels=True ,node_color = node_color)
    num_nodes = len(graph.nodes())
    shift_pos = { 6 : 0.1, 16: 0.15, 30: 0.2,48: 0.2, 70 : 0.3, 96: 0.4}
    if num_nodes < 900:
        length = nx.get_edge_attributes(graph,'length')
        labels = {edge : f"{length[edge]}" for edge in graph.edges()}
        if num_nodes in shift_pos:
            nx.draw_networkx_edge_labels(graph,pos = init_pos, edge_labels = labels, font_size = 10)

        if num_nodes in shift_pos:
            shift = shift_pos[num_nodes]
        else:
            shift = 0.4
        shifted_pos ={node: (node_pos[0],node_pos[1] - shift) for node, node_pos in init_pos.items()}
        node_labels = {node: str([data["penalty"]]) if "penalty" in data else "" for node,data in graph.nodes(data = True)}
        # nx.draw_networkx_labels(G, shifted_pos, labels=node_labels, horizontalalignment="left", font_color = start_colour)
        nx.draw_networkx_labels(graph, shifted_pos, labels=node_labels)

def make_weights_int(graph):
    graph = graph.copy()
    for (u, v) in graph.edges():
        if 'length' in graph[u][v]:
            graph[u][v]['length'] = int(float(graph[u][v]['length']))
        if 'travel_time' in graph[u][v]:
            graph[u][v]['travel_time'] = int(float(graph[u][v]['travel_time']))
    return graph

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
    
folder_hexagons = ".\graphs\input\\"
hexagons = sorted(glob.glob(f"{folder_hexagons}*.graphml"))
folder_cities = ".\cities\output-subsamples\\nl\\"
cities = sorted(glob.glob(f"{folder_cities}*.graphml"))
files =  hexagons + cities
# files.sort(key=os.path.getmtime)
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
    generate_constraints_for_sp(graph, source, target, name)
    generate_constraints_for_tcsp(graph, source, target, name)       
    generate_constraints_for_rcsp(graph, source, target, name)
    generate_constraints_for_ncsp(graph, source, target, name)
    plt.show(block=False)
    plt.pause(0.1)
    plt.close()
