## Deamon that compile GraphViz script into image and display it automatically when the script file is modified
# @author David Dorchies
# @date 07/07/2016

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (QToolTip, QPushButton)
from PyQt5.QtGui import QFont
from interface import Example
import os
import sys
from buildgraph import get_route, get__points, \
    get_pos_agent, math_position, make_dot, lst_optimal, parsing_points, update_graph
from project.dijkstra import dijkstra
from project.math_route import MathRoute

## Read a section in an .ini file and return a dictionnary
#  @param sIniFile Path to the .ini file to read
#  @param sSection Section name to read in the .ini file
#  @return Dictionnary of strings made from couples (key, value)
def GetItemsIniFile(sIniFile, sSection):
    import configparser as cp
    CfgPrm = cp.ConfigParser()
    CfgPrm.read(sIniFile)
    # initialisation de dPrm : dictionnaire des paramètres généraux de la compilation
    dPrm = {}
    if not CfgPrm.has_section(sSection):
        return {}
    for item in CfgPrm.items(sSection):
        dPrm[item[0]] = item[1]
    return dPrm


## Class that add the daemon to the QLabel object


class myLabel(QtWidgets.QLabel):

    def __init__(self, parent=None):
        super(myLabel, self).__init__(parent)
        # Load parameters in dotd.ini
        self.secondWin = None
        self.thirdWin = None
        self.dDOT = GetItemsIniFile("dotd.ini", "DOT")
        self.mTime = 0  # Last modified file time
        self.num_step = 0
        self.pos_x_point = 0
        self.pos_y_point = 0
        self.step = False
        self.pos_x_next_point = 0
        self.pos_y_next_point = 0
        self.next_point = []
        self.supply = []
        self.consumption = []
        self. point = []
        self.all_route = []
        self.count = 0
    ## Daemon that run the GraphViz dot tool and display the image in a QLabel window
    def daemon(self):
        from subprocess import call
        from PyQt5 import QtGui
        import datetime

        dot = "pydot.dot"
        QToolTip.setFont(QFont('SansSerif', 10))
        btn = QPushButton('Выбрать маршрут', self)
        btn.resize(btn.sizeHint())
        btn.move(0, 0)
        btn.clicked.connect(self.openWin)
        if self.step == True:
            self.step_date()
        btn_step = QPushButton('Шаг', self)
        btn_step.resize(btn_step.sizeHint())
        btn_step.move(100, 0)
        btn_step.clicked.connect(self.step_date)

        btn_math_route = QPushButton('Расчет маршрута', self)
        btn_math_route.resize(btn_math_route.sizeHint())
        btn_math_route.move(170, 0)
        btn_math_route.clicked.connect(self.message_box)

        if self.mTime != os.path.getmtime(dot):
            # Run DOT
            tRunDOT = "{0} -T{1} \"{2}\" -o \"{2}.{1}\"".format(self.dDOT["exe"], self.dDOT["format"], dot)
            call(tRunDOT)
            self.setWindowTitle("GraphViz {}.{} {}".format(dot, self.dDOT["format"], datetime.datetime.fromtimestamp(
                os.path.getmtime(dot)).strftime('%Y-%m-%d %H:%M:%S')))
            pixmap = QtGui.QPixmap("{}.{}".format(dot, self.dDOT["format"]))
            self.setPixmap(pixmap)
            self.setStyleSheet("""background-color: #ffffff""")
            self.setFixedSize(pixmap.width(), pixmap.height() + 45)
            self.show()
            self.mTime = os.path.getmtime(dot)

    def openWin(self):
        if not self.secondWin:
            self.secondWin = Example(self)
        self.secondWin.show()

    def message_box(self):
        if not self.thirdWin:
            self.thirdWin = MathRoute(self)
        self.thirdWin.show()

    def step_date(self):

        if self.count < 1:
            self.all_route = get_route()
            self.count = self.count + 1
        if self.step == False:
            for route in self.all_route:
                self.all_route = self.all_route[1:]
                agent_points, self.supply, self.consumption, self.next_point, self.point = get__points(route)
                for agent in agent_points:
                    self.pos_x_point, self.pos_y_point, self.pos_x_next_point, self.pos_y_next_point = get_pos_agent(agent)
                    if self.pos_x_point != self.pos_x_next_point or self.pos_y_point != self.pos_y_next_point:
                        self.step = True
                        pos_x_point, pos_y_point, img_truck = math_position(self.pos_x_point, self.pos_y_point,
                                                                        self.pos_x_next_point,
                                                                        self.pos_y_next_point)
                        dot_step = make_dot()
                        optimal = dijkstra(self.next_point, self.supply, self.consumption)
                        lst_pars = lst_optimal(optimal)
                        parsing_points(self.point, dot_step, lst=[], pos_x_point=pos_x_point, pos_y_point=pos_y_point,
                                       img_truck=img_truck)
                        update_graph(lst_pars, self.next_point, dot_step)
                        walk = os.getcwd()
                        write = open('%s/pydot.dot' % walk, 'w', encoding="UTF-8")
                        write.write(dot_step.source)
                        write.close()
                        return
        else:
            if round(self.pos_x_point) != self.pos_x_next_point or round(self.pos_y_point) != self.pos_y_next_point:
                self.step = True
                self.pos_x_point, self.pos_y_point, img_truck = math_position(self.pos_x_point, self.pos_y_point,
                                                                              self.pos_x_next_point,
                                                                              self.pos_y_next_point)
                dot_step = make_dot()
                optimal = dijkstra(self.next_point, self.supply, self.consumption)
                lst_pars = lst_optimal(optimal)
                parsing_points(self.point, dot_step, lst=[], pos_x_point=self.pos_x_point, pos_y_point=self.pos_y_point,
                               img_truck=img_truck)
                update_graph(lst_pars, self.next_point, dot_step)
                walk = os.getcwd()
                write = open('%s/pydot.dot' % walk, 'w', encoding="UTF-8")
                write.write(dot_step.source)
                write.close()
                return
            else:
                self.step = False
            return
## Main program
def draw():
    from PyQt5 import QtCore
    from interface import Example
    # Define script path (Cf. http://diveintopython.adrahon.org/functional_programming/finding_the_path.html)
    sCurrentPath = os.path.abspath(os.path.dirname(sys.argv[0]))
    os.chdir(sCurrentPath)

    # Bootstraping QT GUI
    app = QtWidgets.QApplication(sys.argv)
    label = myLabel()

    # Defining loop timer for the daemon
    timer = QtCore.QTimer()
    timer.timeout.connect(label.daemon)
    dDaemon = GetItemsIniFile("dotd.ini", "DAEMON")
    timer.start(int(dDaemon["sleep"]))

    # Exit script when the window is closed
    sys.exit(app.exec_())


if __name__ == '__main__':
    draw()
