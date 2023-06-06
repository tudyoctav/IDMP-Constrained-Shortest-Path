import networkx as nx
import matplotlib.pyplot as plt
import random
import sys

def add_random_weights(G):
    N = len(G.nodes())
    for n in G.nodes():
        # generate random lower bound
        G.nodes[n]['lower_bound'] = random.randint(0,5)
        # generate random upper bound
        G.nodes[n]['upper_bound'] = G.nodes[n]['lower_bound'] + random.randint(1,3) * N

    for (u, v) in G.edges():
        # generate random distance
        distance = random.randint(2,5)
        # generate random time by altering the distance
        time = distance + random.randint(-2,5)
        G[u][v]['weight'] = distance
        G[u][v]['time'] = time
        # generate appropriate lower bound and upper bound
        # G[u]['lower bound'] += int(G[u][v]['weight']  * random.lognormvariate(0,1))
        G.nodes[v]['upper_bound'] = max(G.nodes[v]['upper_bound'], G.nodes[u]['upper_bound'] + int(time * random.uniform(1,2)))
        # generate appropriate colour
        if time < 2:
            colour = 'lightgreen'
        elif time < 4 :
            colour = 'green'
        elif time < 5 :
            colour = 'darkgreen'
        elif time < 6 :
            colour = 'yellow'
        elif time < 7 :
            colour = 'orange'
        elif time < 8 :
            colour = 'darkred'
        else:
            colour = 'red'
        # colour = 'black'
        G[u][v]['colour'] = colour

options = {
    # 'node_color': 'black',
    'node_size': 100,
    'width': 3,
    'with_labels' : True,
}

def relable_tuple_nodes(G):
    mapping = {}
    ind = 0
    for (left,right) in G.nodes():
        mapping[(left,right)] = ind
        ind += 1
    # for (left,right) in G.nodes():
    #     mapping[(left,right)] = str(left) + ',' + str(right)
    nx.relabel_nodes(G, mapping, copy = False)

def remove_pos(G):
    for _,val in G.nodes().items():
        if 'pos' in val:
            del val['pos']

# star graph
G = nx.petersen_graph()
add_random_weights(G)
subax1 = plt.subplot(231)
subax1.set_title('Peterson graph')
nx.draw_shell(G, nlist=[range(5, 10), range(5)], **options)
edges = G.edges()
colors = [G[u][v]['colour'] for u,v in edges]
# nx.draw_spectral(G, edge_color=colors, **options)
# nx.write_graphml(G, "./graphs/petersen.graphml", named_key_ids=True)

# dodecahedral graph
G = nx.dodecahedral_graph()

add_random_weights(G)
subax2 = plt.subplot(232)
subax2.set_title('Dodecahedral graph')
shells = [[2, 3, 4, 5, 6], [8, 1, 0, 19, 18, 17, 16, 15, 14, 7], [9, 10, 11, 12, 13]]
# nx.draw_shell(G, nlist=shells, **options)
edges = G.edges()
colors = [G[u][v]['colour'] for u,v in edges]
nx.draw_spectral(G, **options)
# nx.write_graphml(G, "./graphs/dodecahedral.graphml", named_key_ids=True)

# Dorogovtsev-Goltsev-Mendes graph
G = nx.dorogovtsev_goltsev_mendes_graph(3)
pos = nx.get_node_attributes(G, 'pos')
init_pos = {key:np.array([x,y]) for key,(x,y) in nx.get_node_attributes(G, 'pos').items()}
pos = nx.kamada_kawai_layout(G)
subax3 = plt.subplot(233)
subax3.set_title('Dorogovtsev-Goltsev-Mendes graph (n = 3)')
edges = G.edges()
# colors = [G[u][v]['colour'] for u,v in edges]
nx.draw(G, pos,**options)
# nx.write_graphml(G, "./graphs/dorogovtsev_goltsev_mendes.graphml", named_key_ids=True)

# Triangular lattice graph
G = nx.triangular_lattice_graph(5, 5)
relable_tuple_nodes(G)
# add_random_weights(G)
subax4 = plt.subplot(234)
subax4.set_title('Triangular lattice (5,5)')
print(len(G.nodes()))
edges = G.edges()
# colors = [G[u][v]['colour'] for u,v in edges]
pos = {ind:val["pos"] for ind,val in G.nodes().items()}
nx.draw(G, pos = pos, **options)
# nx.write_graphml(G, "./graphs/triangular_lattice.graphml", named_key_ids=True)

# Grid graph
G=nx.grid_graph(dim=[5,5])  # 5x5 grid
relable_tuple_nodes(G)
# add_random_weights(G)
subax5 = plt.subplot(235)
subax5.set_title('Grid graph (5,5)')
edges = G.edges()
# colors = [G[u][v]['colour'] for u,v in edges]
pos = {val[0]:val[1]["pos"] for val in G.nodes(data=True)}
nx.draw(G,pos=pos,  **options)
remove_pos(G)
# nx.write_graphml(G, "./graphs/grid.graphml", named_key_ids=True)

# Hexagonal lattice graph
G = nx.hexagonal_lattice_graph(3, 3)
relable_tuple_nodes(G)
# add_random_weights(G)
subax6 = plt.subplot(236)
subax6.set_title('Hexagonal lattice (3,3)')
edges = G.edges()
# colors = [G[u][v]['colour'] for u,v in edges]
pos = {ind:val["pos"] for ind,val in G.nodes().items()}
nx.draw(G, pos=pos, **options)
remove_pos(G)
# nx.write_graphml(G, "./graphs/hexagonal_lattice.graphml", named_key_ids=True)
plt.show()