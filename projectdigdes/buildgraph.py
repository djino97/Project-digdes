"""
Buildgraph module is intended for graph construction.
"""

from graphviz import Digraph
import os
import subprocess
from database.query import session_create, \
    session_clear_field, session_add_pos, \
    session_get_pos, session_add_route, session_get_routs,\
    session_get_agents, get_id_supply_consumption, session_get_pos_point
from dijkstra import dijkstra
import random


def make_dot():
    """
    The graphviz module provides two classes: Graph and Digraph.
     They create graph descriptions in the DOT language for undirected and directed graphs respectively.
    :return:dot
    """
    dot = Digraph(comment='Logistics', graph_attr=dict(size="100,100", layout='neato'),
                  node_attr=dict(style='filled', fontsize='20',
                                 height='0.9', weight='20'))
    dot.node_attr.update(color='lightblue2', style='filled')
    dot.attr(bgcolor='purple:pink', label='Logistics',
             fontcolor='white', ranksep='1', nodesep='1.5')
    return dot


def parsing_points(state, dot):
    """
    The node()-method takes a "name" identifier as first argument and an optional "label".
    :param state:
    :param dot:
    :return:nothing
    """
    for point in state:
        pos_x = 0
        n_x = 0
        n_y = 0
        pos_y = 0
        while pos_x == n_x and pos_y == n_y:
            n_x = random.randint(0, 14)
            n_y = random.randint(0, 10)
        pos_x = n_x
        pos_y = n_y
        pos = '{0},{1}!'.format(pos_x, pos_y)
        session_add_pos(pos, point)
        dot.node('%s' % point.id_point, label='%s' % point.name_point, pos=pos)


def update_point_graph(state, dot):
    """
        The node()-method takes a "name" identifier as first argument and an optional "label".
        :param state:
        :param dot:
        :return:nothing
        """
    truck = True
    for point in state:
        position_point = session_get_pos(point)
        for pos in position_point:
            dot.node('%s' % point.id_point, label='%s' % point.name_point, pos=pos.pos_x_and_y)
            # If this vertex is supply then the image of the truck is put in these coordinates
            if truck:
                dot.node(' ', label='<<TABLE><TR><TD><IMG SRC="truck_right.png"/></TD></TR></TABLE>>',
                         pos=pos.pos_x_and_y, shape='plaintext', style='')
                truck = False


def put_truck(dot, pos_x_image, pos_y_image, img_truck):
    """
    Image of the truck is put in given coordinates
    :param dot:
    :param pos_x_image:
    :param pos_y_image:
    :param img_truck:left or right image truck
    :return: nothing
    """
    if img_truck == 'truck_right':
            dot.node(' ', label='<<TABLE><TR><TD><IMG SRC="truck_right.png"/></TD></TR></TABLE>>',
                     pos='{0},{1}!'.format(pos_x_image, pos_y_image),
                     shape='plaintext', style='')
    else:
        dot.node(' ', label='<<TABLE><TR><TD><IMG SRC="truck_left.png"/></TD></TR></TABLE>>',
                 pos='{0},{1}!'.format(pos_x_image, pos_y_image),
                 shape='plaintext', style='')


def parsing_next_point(state, dot):
    """
    The edge()-method takes the names of start- and end-node, while edges() takes iterable of name-pairs.
    :param state: point from the table NextPoint
    :param dot:
    :return: nothing
    """
    for elements in state:
        dot.edge('%s' % elements.id_point, '%s' % elements.id_next_point, label='%s' % elements.distance)


def lst_optimal(lst):
    """
    Splitting a list into lists of two elements
    Example, [1, 2, 3] -> [[1, 2], [2, 3]]
    :param lst: getting function dijkstra
    :return:lists of two elements
    """
    return [lst[i:i + 2] for i in range(0, len(lst) - 1)]


def update_graph(lst_pars, point, dot_update):
    """
    Update edges and route designation red color
    :param lst_pars:
    :param point:
    :param dot_update:
    :return:nothing
    """
    restore = lst_pars
    for next_point in point:
            for optimal_point in lst_pars:
                if optimal_point[0] == next_point.id_point and optimal_point[1] == next_point.id_next_point:
                    dot_update.edge('%s' % optimal_point[0], '%s' % optimal_point[1], label='%s' % next_point.distance,
                                    color='red', penwidth='2.0', )
                    break
                lst_pars = lst_pars[1:]
                if not lst_pars:
                    dot_update.edge('%s' % next_point.id_point, '%s' % next_point.id_next_point,
                                    label='%s' % next_point.distance)
                    lst_pars = restore
    return


def main():
    """
    Creating graph with the first markup points
    :return: nothing
    """
    dot = make_dot()
    session_clear_field()
    next_point, point, warehouse = session_create()
    parsing_points(point, dot)
    parsing_next_point(next_point, dot)
    f = open('testoutput/pydot.dot', 'w', encoding="UTF-8")
    f.write(dot.source)
    f.close()
    walk = os.getcwd()
    subprocess.Popen("%s/testoutput/dotd.py" % walk, shell=True)


def update_graphic(id_supply, id_consumption, route, empty_truck):
    """
    Updating the graph when laying the route
    :param id_supply: source point
    :param id_consumption: target point
    :param route:
    :param empty_truck:
    :return: nothing
    """
    next_point, point, warehouse = session_create()
    dot_update = make_dot()
    optimal = dijkstra(next_point, id_supply, id_consumption)
    lst_pars = lst_optimal(optimal)
    update_point_graph(point, dot_update)
    update_graph(lst_pars, next_point, dot_update)
    walk = os.getcwd()
    write = open('%s/pydot.dot' % walk, 'w', encoding="UTF-8")
    write.write(dot_update.source)
    write.close()
    session_add_route(lst_pars, route, id_supply, empty_truck)


def position_par(point):
    """
    Getting position x and y point route from the Point
    table attribute pos_x_and_y
    :param point: all
    :return: position x, y
    """
    lst = []
    lst_x = []
    lst_y = []
    for pos in point:
        for str_pos in pos.pos_x_and_y:
            if str_pos == ',':
                lst_x = lst
                lst = []

            elif str_pos == '!':
                lst_y = lst
                lst = []
            else:
                lst.append(str_pos)
    pos_x = int(''.join(map(str, lst_x)))
    pos_y = int(''.join(map(str, lst_y)))
    return pos_x, pos_y


def get_route():
    all_route = session_get_routs()
    return all_route


def get__points(route):
    agent_points = session_get_agents(route.id_agent)
    supply, consumption = get_id_supply_consumption(route.num_party)
    next_point, point, warehouse = session_create()
    return [agent_points, supply, consumption, next_point, point]


def get_pos_agent(agent):
    pos_point, pos_next_point = session_get_pos_point(agent.id_point, agent.id_next_point)
    pos_x_next_point, pos_y_next_point = position_par(pos_next_point)
    pos_x_point, pos_y_point = position_par(pos_point)
    return [pos_x_point, pos_y_point, pos_x_next_point, pos_y_next_point]


def math_position(pos_x_point, pos_y_point, pos_x_next_point, pos_y_next_point):
    """
    Calculation of the position for the truck
    :param pos_x_point: position x for start point
    :param pos_y_point: position y for start point
    :param pos_x_next_point: position x for start point
    :param pos_y_next_point: position y for end point
    :return:position x and y for truck, image truck
    """
    delta_x = pos_x_next_point - pos_x_point
    delta_y = pos_y_next_point - pos_y_point
    if delta_x == 0:
        if delta_y < 0:
            pos_y_point = pos_y_point - 1 * 0.05
            img_truck = 'truck_left.png'
        else:
            pos_y_point = pos_y_point + 1 * 0.05
            img_truck = 'truck_right.png'
        return pos_x_point, pos_y_point, img_truck
    elif delta_y == 0:
        if delta_x < 0:
            pos_x_point = pos_x_point - 1 * 0.05
            img_truck = 'truck_left.png'
        else:
            pos_x_point = pos_x_point + 1 * 0.05
            img_truck = 'truck_right.png'
        return pos_x_point, pos_y_point, img_truck

    if abs(delta_x) > abs(delta_y):
        step_truck_x = (delta_x / delta_y) * 0.05
        if delta_x < 0:
            pos_x_point = pos_x_point - abs(step_truck_x)
            img_truck = 'truck_left.png'
        else:
            pos_x_point = pos_x_point + abs(step_truck_x)
            img_truck = 'truck_right.png'
        if delta_y < 0:
            pos_y_point = pos_y_point - 1 * 0.05
        else:
            pos_y_point = pos_y_point + 1 * 0.05
    else:
        step_truck_y = (delta_y / delta_x) * 0.05
        if delta_x < 0:
            pos_x_point = pos_x_point - 1 * 0.05
            img_truck = 'truck_left.png'
        else:
            pos_x_point = pos_x_point + 1 * 0.05
            img_truck = 'truck_right.png'
        if delta_y < 0:
            pos_y_point = pos_y_point - abs(step_truck_y)
        else:
            pos_y_point = pos_y_point + abs(step_truck_y)
    return pos_x_point, pos_y_point, img_truck


if __name__ == '__main__':
    main()
