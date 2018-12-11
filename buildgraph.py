"""
Buildgraph module is intended for graph construction
"""

from graphviz import Digraph
import os
import subprocess
from database.query import session_create


def make_dot():
    dot = Digraph(comment='Logistics', graph_attr=dict(size="100,100"),
                  node_attr=dict(style='filled', fontsize='20',
                                 height='0.9', weight='20'))
    dot.node_attr.update(color='lightblue2', style='filled')
    dot.attr(bgcolor='purple:pink', label='Logistics',
             fontcolor='white', ranksep='1', nodesep='1.5')
    return dot


def pars(elements, dot):
    dot.edge('%s' % elements[0], '%s' % elements[1], label='%s' % elements[2],
             weight='%s' % (elements[2] * 0.1))


def parsing(state, dot):
    for val in state:
        pars(val, dot)


def main():
    dot = make_dot()
    state = session_create()
    parsing(state, dot)

    f = open('testoutput/roundtable.gv', 'w')
    f.write(dot.source)
    f.close()
    walk = os.getcwd()
    subprocess.Popen("%s/testoutput/dotd.py" % walk, shell=True)


if __name__ == '__main__':
    main()
