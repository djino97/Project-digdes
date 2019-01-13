"""
Dijkstra module calculates shortest way between two points
"""
import networkx as nx

graph = nx.Graph().to_directed()


def pars(node1, node2, weight):
    """
    Creating graph for networkx
    :param node1:start point
    :param node2: end point
    :param weight: distance
    :return:
    """
    graph.add_edge(node1, node2, weight=weight)
    return


def parsing(state):
    for val in state:
        pars(val.id_point, val.id_next_point, val.distance)


def dijkstra(supply_point, consumption_point):
    """
    Function returns shortest way between two points
    :param supply_point:source point
    :param consumption_point:target point
    :return: shortest way between two points
    """
    for source in supply_point:
        for target in consumption_point:
            return nx.dijkstra_path(graph, source.id_point, target.id_point)


def dijkstra_warehouse(id_warehouse, id_supply, id_consumption):
    memory = 0
    route = []
    flag = True
    warehouse_point = 0
    for supply in id_supply:
        for consumption in id_consumption:
            for warehouse in id_warehouse:
                length_one, list_one = nx.bidirectional_dijkstra(graph, supply.id_point, warehouse.id_point)
                length_two, list_two = nx.bidirectional_dijkstra(graph, warehouse.id_point, consumption.id_point)
                sum_length = length_one + length_two
                if sum_length < memory or flag is True:
                    memory = sum_length
                    flag = False
                    list_one.extend(list_two[1:])
                    route = list_one
                    warehouse_point = warehouse.id_point
    return route, warehouse_point



