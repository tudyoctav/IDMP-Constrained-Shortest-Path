import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import random
import sys

def remove_random_edges(G, p = 0.1):
    G_copy = G.copy()
    res = 0
    for (u, v) in G.edges():
        if random.random() < p:
            res = res + 1
            G_copy.remove_edge(u, v)
    print("Removed ", res, " edges")
    if nx.is_connected(G_copy):
        return G_copy
    else:
        print("Graph is not connected, retrying")
        return remove_random_edges(G, p = p)

def add_random_lengths(G , pos = None, scale = 100, var = 0):
    N = len(G.nodes())

    for (u, v) in G.edges():
        # generate random length
        if pos:
            length = max(1,int(np.sum(np.square(pos[u] - pos[v])) * scale) + random.randint(-var,var))
            # print("Raw",np.sum(np.square(pos[u] - pos[v])))
            # print("Scaled", np.sum(np.square(pos[u] - pos[v])) * scale)
            # print("Length", length)
        else:
            length = random.randint(3,10)
        G[u][v]['length'] = length
  
def relable_tuple_nodes(G, custom = None):
    mapping = {}
    ind = 1
    custom = custom if custom else range(len(G.nodes()) + 1)
    for (left,right) in G.nodes():
        mapping[(left,right)] = custom[ind]
        ind += 1
    # for (left,right) in G.nodes():
    #     mapping[(left,right)] = str(left) + ',' + str(right)
    nx.relabel_nodes(G, mapping, copy = False)
    return ind - 1

def add_pos_to_nodes(G, pos):
    for node in G.nodes():
        G.nodes[node]['x'] = pos[node][0]
        G.nodes[node]['y'] = pos[node][1]

def remove_pos(G):
    for _,val in G.nodes().items():
        if 'pos' in val:
            del val['pos']

def ask_yes_no_question(question):
    while True:
        user_input = input(question + " (Y/N): ").upper()
        if user_input == "Y":
            return True
        elif user_input == "N":
            return False
        else:
            print("Invalid input. Please enter Y or N.")
            ask_yes_no_question(question)
def generate_graph(N = 10, scale = 10, var = 9, p = 0.1, draw_edge_labels = False, draw_node_labels = False, save = None):

    
    options = {
        # 'node_color': 'black',
        'node_size': 100,
        'width': 3,
        'with_labels' : draw_node_labels,
        'font_size' : 8,
    }


    p = p if N > 1 else 0
    # fig = plt.gcf()
    plt.clf()
    plt.cla()
    plt.close()
    fig = plt.figure(f"Network generation", figsize=(17,10))
    start_colour = 'mediumorchid'
    G = nx.hexagonal_lattice_graph(N, N)
    start_node = 1
    end_node = relable_tuple_nodes(G)
    G.graph["start_node"] = start_node
    G.graph["finish_node"] = end_node
    subax1 = plt.subplot(2,2,1)
    subax1.set_title(f'Hexagonal lattice ({N},{N})')
    # Extract the positions
    pos = nx.get_node_attributes(G, 'pos')
    init_pos = {key:np.array([x,y]) for key,(x,y) in nx.get_node_attributes(G, 'pos').items()}
    # G = add_pos_to_nodes(G, init_pos)
    shortestPath = nx.shortest_path(G, source = start_node, target = end_node)
    node_colors = ["red" if n in shortestPath else "tab:blue" for n in G.nodes()]
    node_colors[start_node - 1] = start_colour
    node_colors[end_node - 1] = start_colour
    nx.draw(G, pos, node_color=node_colors, **options)

    # shifted_pos ={node: node_pos for node, node_pos in init_pos.items()}
    # shifted_pos[start_node - 1] = shifted_pos[start_node - 1] + np.array([0,-1])
    # shifted_pos[end_node - 1] = shifted_pos[end_node - 1] + np.array([0,0.7])
    # node_labels = {}
    # node_labels[0] = 'Start'
    # node_labels[num_nodes - 1] = 'End'
    # nx.draw_networkx_labels(G, shifted_pos, labels=node_labels, horizontalalignment="left", font_color = start_colour)



    # add lengths
    add_random_lengths(G, pos = init_pos, scale = scale, var = 0)
    subax2 = plt.subplot(2,2,2)
    subax2.set_title('Adding scaled lengths to edges')
    #edges = G.edges()
    # colors = [G[u][v]['colour'] for u,v in edges]
    pos = nx.kamada_kawai_layout(G, pos = init_pos, weight='length')
    shortestPath = nx.shortest_path(G, source = start_node, target = end_node, weight='length')
    node_colors = ["red" if n in shortestPath else "tab:blue" for n in G.nodes()]
    node_colors[start_node - 1] = start_colour
    node_colors[end_node - 1] = start_colour
    nx.draw(G, pos,node_color=node_colors, **options)
    if draw_edge_labels:
        labels = nx.get_edge_attributes(G,'length')
        nx.draw_networkx_edge_labels(G,pos = pos, edge_labels = labels, font_size = 6)

    # add variance
    add_random_lengths(G, pos = init_pos, scale = scale, var = var)
    subax3 = plt.subplot(2,2,3)
    subax3.set_title('Adding variance to edges')
    #edges = G.edges()
    # colors = [G[u][v]['colour'] for u,v in edges]
    pos = nx.kamada_kawai_layout(G, pos = init_pos, weight='length')
    shortestPath = nx.shortest_path(G, source = start_node, target = end_node, weight='length')
    node_colors = ["red" if n in shortestPath else "tab:blue" for n in G.nodes()]
    node_colors[start_node - 1] = start_colour
    node_colors[end_node - 1] = start_colour
    nx.draw(G, pos,node_color=node_colors, **options)
    if draw_edge_labels:
        labels = nx.get_edge_attributes(G,'length')
        nx.draw_networkx_edge_labels(G,pos = pos, edge_labels = labels, font_size = 6)

    subax4 = plt.subplot(2,2,4)
    subax4.set_title(f'Removing edges with p = {p}')
    G = remove_random_edges(G, p)
    pos = nx.kamada_kawai_layout(G, pos = init_pos, weight='length')
    shortestPath = nx.shortest_path(G, source = start_node, target = end_node, weight='length')
    node_colors = ["red" if n in shortestPath else "tab:blue" for n in G.nodes()]
    node_colors[start_node - 1] = start_colour
    node_colors[end_node - 1] = start_colour
    nx.draw(G, pos, node_color=node_colors, **options)
    if draw_edge_labels:
        labels = nx.get_edge_attributes(G,'length')
        nx.draw_networkx_edge_labels(G,pos = pos, edge_labels = labels, font_size = 6)

    # draw just the final graph
    fig2 = plt.figure(f"Final network", figsize = (17,10))
    fig2.suptitle(f"Network with |V| = {G.number_of_nodes()} and |E| = {G.number_of_edges()}")
    nx.draw(G, pos, node_color=node_colors, **options)
    if draw_edge_labels:
        labels = nx.get_edge_attributes(G,'length')
        nx.draw_networkx_edge_labels(G,pos = pos, edge_labels = labels, font_size = 6)

    # colors = [G[u][v]['colour'] for u,v in edges]
    plt.show(block = False)
    plt.pause(1)
    plt.close()
    if save or ask_yes_no_question("Do you want to save the graph and image?"):
        name = f"hexagonal_lattice_N_{N}"
        G.graph['name'] = name
        remove_pos(G)
        add_pos_to_nodes(G, init_pos)
        print(f"Saving graph as {name}")
        nx.write_graphml(G, f"./graphs/input/{name}.graphml", named_key_ids=True)
        fig.savefig(f"./images/graph_generation/{name}.png")
        fig2.savefig(f"./images/input/{name}.png")

def main():
    # generate_graph(N = 1, p = 0, draw_edge_labels= True, draw_node_labels = True, save = False)
    # for N in range(2,5):
    #     generate_graph(N = N, p = 0.10, draw_edge_labels= True, draw_node_labels = True, save = False)
    # for N in range(5, 10):
    #     generate_graph(N = N, p = 0.20, draw_node_labels = True, save = True)
    for N in range(10, 21):
            generate_graph(N = N, p = 0.15, save = True)
    # for N in range(20, 30):
    #         generate_graph(N = N, p = 0.10, save = True)
if __name__ == "__main__":
    main()