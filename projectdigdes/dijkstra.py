"""
Dijkstra module calculates shortest way between two points
"""
import networkx as nx


def pars(node1, node2, weight, graph):
    """
    Creating graph for networkx
    :param node1:start point
    :param node2: end point
    :param weight: distance
    :param graph: initialized graph
    :return:
    """
    graph.add_edge(node1, node2, weight=weight)
    return


def parsing(state, graph):
    for val in state:
        pars(val.id_point, val.id_next_point, val.distance, graph)


def dijkstra(agent, supply_point, consumption_point):
    """
    Function returns shortest way between two points
    :param agent: tuples from table NextPoint
    :param supply_point:source point
    :param consumption_point:target point
    :return: shortest way between two points
    """
    graph = nx.Graph().to_directed()
    parsing(agent, graph)
    for source in supply_point:
        for target in consumption_point:
            return nx.dijkstra_path(graph, source.id_point, target.id_point)
