# Deamon that compile GraphViz script into image and display it automatically when the script file is modified
# @author David Dorchies
# @date 07/07/2016

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (QToolTip, QPushButton, QLabel)
from PyQt5.QtGui import QFont
from interface import Example
import os
import sys
from buildgraph import get_route, get__points, \
    get_pos_agent, math_position, make_dot, update_graph, \
    put_truck, update_point_graph, get_date_supply, update_graphic, main
from project.math_route import MathRoute
from search_route import list_routs
import datetime

# Read a section in an .ini file and return a dictionnary
#  @param s_ini_file Path to the .ini file to read
#  @param s_section Section name to read in the .ini file
#  @return Dictionnary of strings made from couples (key, value)


def get_items_ini_file(s_ini_file, s_section):
    import configparser as cp
    cfg_prm = cp.ConfigParser()
    cfg_prm.read(s_ini_file)
    # initialisation de d_prm : dictionnaire des paramètres généraux de la compilation
    d_prm = {}
    if not cfg_prm.has_section(s_section):
        return {}
    for item in cfg_prm.items(s_section):
        d_prm[item[0]] = item[1]
    return d_prm


# Class that add the daemon to the QLabel object


class MyLabel(QtWidgets.QLabel):

    def __init__(self, parent=None):
        super(MyLabel, self).__init__(parent)
        # Load parameters in dotd.ini
        self.secondWin = None
        self.thirdWin = None
        self.dDOT = get_items_ini_file("dotd.ini", "DOT")
        self.mTime = 0  # Last modified file time
        self.num_step = 0
        self.pos_x_point = 0
        self.pos_y_point = 0
        self.ride_truck = False
        self.step = False
        self.pos_x_next_point = 0
        self.pos_y_next_point = 0
        self.next_point = []
        self.supply = []
        self.position_truck = []
        self.consumption = []
        self. point = []
        self.add_truck = []
        self.count_agent_route = 1
        self.all_route = []
        self.search_route = True
        self.count_route = 0
        self.date_step, self.date_count_departure, self.date_count_arrival = get_date_supply()

        self.label_route = QLabel("Mаршруты:", self)
        self.label_route.move(295, 0)

        self.btn_step = QPushButton(self)
        self.btn_step.resize(self.btn_step.sizeHint())
        self.btn_step.move(100, 0)
        self.btn_step.clicked.connect(self.step_date)
        
# Daemon that run the GraphViz dot tool and display the image in a QLabel window
    def daemon(self):
        from subprocess import call
        from PyQt5 import QtGui

        dot = "pydot.dot"

        QToolTip.setFont(QFont('SansSerif', 10))
        btn = QPushButton('Выбрать маршрут', self)
        btn.resize(btn.sizeHint())
        btn.move(0, 0)
        btn.clicked.connect(self.open_win)

        if self.step is True:
            self.step_date()

        if self.search_route is True:
            self.update_route()
            self.search_route = False

        btn_math_route = QPushButton('Расчет маршрута', self)
        btn_math_route.resize(btn_math_route.sizeHint())
        btn_math_route.move(189, 0)
        btn_math_route.clicked.connect(self.message_box)

        if self.mTime != os.path.getmtime(dot):
            # Run DOT
            t_run_dot = "{0} -T{1} \"{2}\" -o \"{2}.{1}\"".format(self.dDOT["exe"], self.dDOT["format"], dot)
            call(t_run_dot)
            self.setWindowTitle("GraphViz {}.{} {}".format(dot, self.dDOT["format"], datetime.datetime.fromtimestamp(
                os.path.getmtime(dot)).strftime('%Y-%m-%d %H:%M:%S')))
            pixmap = QtGui.QPixmap("{}.{}".format(dot, self.dDOT["format"]))
            self.setPixmap(pixmap)
            self.setStyleSheet("""background-color: #ffffff""")
            self.setFixedSize(pixmap.width(), pixmap.height() + 45)
            self.show()
            self.mTime = os.path.getmtime(dot)

    def update_route(self):
        str_route, check = list_routs()
        self.label_route.setText(str_route)
        self.label_route.adjustSize()
        self.date_step, self.date_count_departure, self.date_count_arrival = get_date_supply()
        if self.date_step:
            self.btn_step.setText('Шаг %s' % self.date_step.strftime('%d-%m-%Y'))
        else:
            self.btn_step.setText('Шаг  не задан')
        self.btn_step.adjustSize()
        self.count_agent_route = 1
        if check != 0:
            update_graphic()
        else:
            main()

    def open_win(self):
        if not self.secondWin:
            self.secondWin = Example(self)
            self.secondWin.trigger.connect(self.update_route)
        self.secondWin.show()

    def message_box(self):
        if not self.thirdWin:
            self.thirdWin = MathRoute(self)
        self.thirdWin.show()

    def step_date(self):
        """
        The method is called when pressing the button step,
        then the truck passes one agent. If true, the method is called
        from the main code automatically.
        :return:if truck passes one agent, then return "True",
        else "False"
        """
        if not self.ride_truck and self.date_count_arrival != self.date_count_departure:
            self.all_route = get_route(self.date_count_departure, self.count_agent_route)
            self.step = True
            self.all_route = self.all_route[self.count_route:]
            self.count_route += 1
            for route in self.all_route:
                agent_points, self.supply, self.consumption, self.next_point, self.point = get__points(route)
                for agent in agent_points:
                    self.pos_x_point, self.pos_y_point, self.pos_x_next_point, \
                       self.pos_y_next_point = get_pos_agent(agent)
                    self.ride_truck = True
                    return
            else:
                self.count_route = 0
                self.count_agent_route += 1
                self.step = False
                self.date_count_departure = self.date_count_departure + datetime.timedelta(days=1)
                self.btn_step.setText('Шаг %s' % self.date_count_departure.strftime('%d-%m-%Y'))
                self.btn_step.adjustSize()
                return
        else:
            # truck will not reach the end point, then coordinate calculations are performed
            if round(self.pos_x_point) != self.pos_x_next_point or round(self.pos_y_point) != self.pos_y_next_point:
                self.pos_x_point, self.pos_y_point, img_truck = math_position(self.pos_x_point, self.pos_y_point,
                                                                              self.pos_x_next_point,
                                                                              self.pos_y_next_point)
                dot_step = make_dot()
                update_point_graph(self.point, dot_step, False, ride_truck=self.add_truck,
                                   img_truck=img_truck, supply=self.supply)
                put_truck(dot_step, self.pos_x_point, self.pos_y_point, img_truck)
                update_graph(self.next_point, dot_step)
                walk = os.getcwd()
                write = open('%s/pydot.dot' % walk, 'w', encoding="UTF-8")
                write.write(dot_step.source)
                write.close()
                return
            else:
                self.add_truck = []
                self.add_truck.append(self.pos_x_point)
                self.add_truck.append(self.pos_y_point)
                self.ride_truck = False


# Main program
def draw():
    from PyQt5 import QtCore

    # Define script path (Cf. http://diveintopython.adrahon.org/functional_programming/finding_the_path.html)
    sCurrentPath = os.path.abspath(os.path.dirname(sys.argv[0]))
    os.chdir(sCurrentPath)

    # Bootstraping QT GUI
    app = QtWidgets.QApplication(sys.argv)
    label = MyLabel()

    # Defining loop timer for the daemon
    timer = QtCore.QTimer()
    timer.timeout.connect(label.daemon)
    d_daemon = get_items_ini_file("dotd.ini", "DAEMON")
    timer.start(int(d_daemon["sleep"]))

    # Exit script when the window is closed
    sys.exit(app.exec_())


if __name__ == '__main__':
    draw()
