"""
Buildgraph module is intended for graph construction.
"""

from graphviz import Digraph
import os
import subprocess
from database.query import session_create, session_clear_field, session_add_pos, session_get_pos
from dijkstra import dijkstra
import random


def make_dot():
    dot = Digraph(comment='Logistics', graph_attr=dict(size="100,100", layout='neato'),
                  node_attr=dict(style='filled', fontsize='20',
                                 height='0.9', weight='20'))
    dot.node_attr.update(color='lightblue2', style='filled')
    dot.attr(bgcolor='purple:pink', label='Logistics',
             fontcolor='white', ranksep='1', nodesep='1.5')
    return dot


def parsing_points(state, dot, *args):
    pos_x = 0
    n_x = 0
    n_y = 0
    pos_y = 0
    for point in state:
        if not args:
            while pos_x == n_x and pos_y == n_y:
                n_x = random.randint(0, 15)
                n_y = random.randint(0, 10)
            pos_x = n_x
            pos_y = n_y
            pos = '{0},{1}!'.format(pos_x, pos_y)
            session_add_pos(pos, point)
            dot.node('%s' % point.id_point, label='%s' % point.name_point, pos=pos)
        else:
            position_point = session_get_pos(point)
            for pos in position_point:
                dot.node('%s' % point.id_point, label='%s' % point.name_point, pos=pos.pos_x_and_y)


def parsing_next_point(state, dot):
    for elements in state:
        dot.edge('%s' % elements.id_point, '%s' % elements.id_next_point, label='%s' % elements.distance, dir='back')


def lst_optimal(lst):
    return [lst[i:i + 2] for i in range(0, len(lst) - 1)]


def update_graph(lst_pars, point, dot_update):
    restore = lst_pars
    for next_point in point:
            for optimal_point in lst_pars:
                if optimal_point[0] == next_point.id_point and optimal_point[1] == next_point.id_next_point:
                    dot_update.edge('%s' % optimal_point[0], '%s' % optimal_point[1], label='%s' % next_point.distance,
                                    color='red', penwidth='2.0', dir='back')
                    break
                lst_pars = lst_pars[1:]
                if not lst_pars:
                    dot_update.edge('%s' % next_point.id_point, '%s' % next_point.id_next_point,
                                    label='%s' % next_point.distance, dir='back')
                    lst_pars = restore
    return


def main():
    # buid graph
    dot = make_dot()
    session_clear_field()
    next_point, point, warehouse = session_create()
    parsing_points(point, dot)
    parsing_next_point(next_point, dot)
    f = open('testoutput/pydot.dot', 'w')
    f.write(dot.source)
    f.close()
    walk = os.getcwd()
    subprocess.Popen("%s/testoutput/dotd.py" % walk, shell=True)


def update_graphic(id_supply):
    # update graph dijkstra
    next_point, point, warehouse = session_create()
    dot_update = make_dot()
    parsing_points(point, dot_update, True)
    optimal = dijkstra(next_point, id_supply)
    lst_pars = lst_optimal(optimal)
    update_graph(lst_pars, next_point, dot_update)
    walk = os.getcwd()
    write = open('%s/pydot.dot' % walk, 'w')
    write.write(dot_update.source)
    write.close()


if __name__ == '__main__':
    main()
