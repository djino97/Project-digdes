import networkx as nx
G = nx.Graph().to_directed()


def pars(node1, node2, weight, G):
    G.add_edge(node1, node2, weight=weight)
    return


def parsing(state, G):
    for val in state:
        pars(val.id_point, val.id_next_point, val.distance, G)


def dijkstra(next_point, point_val):
    parsing(next_point, G)
    for source in point_val[1]:
        optimal_distance = nx.dijkstra_path(G, source.id_point, 2)
        return optimal_distance
