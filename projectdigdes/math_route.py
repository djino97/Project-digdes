from PyQt5.QtWidgets import (QWidget, QLabel, QComboBox, QPushButton)
from PyQt5 import QtCore
from database.query import session_get_data_route


class MathRoute(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent, QtCore.Qt.Window)
        self.summ_loading_unloading = 0
        self.coast_loading_unloading = 0
        self.combo_route = QComboBox(self)
        self.combo_route.addItems(['1', '2'])
        self.combo_route.move(180, 25)
        self.initUI()

    def initUI(self):
        lbl_route = QLabel("Выбрать маршрут", self)
        lbl_route.move(80, 25)

        route = self.combo_route.currentText()
        summ_loading_unloading, coast_loading_unloading, coast_distance = math_route(route)
        lbl_supply = QLabel("Суммарное время разгрузки и погрузки партии:{0}, "
                            "расчетная стоимость:{1}".format(summ_loading_unloading,
                                                             coast_loading_unloading), self)
        lbl_supply.move(80, 50)

        lbl_coast_distance = QLabel("Расчет суммы за каждый пройденый километр:{0} ".format(coast_distance), self)
        lbl_coast_distance.move(80, 70)

        self.setGeometry(300, 300, 550, 150)
        self.setWindowTitle('Расчет маршрута')


def math_route(route):
        loading, unloading, distance_route = session_get_data_route(route)
        coast_distance = 0
        for load in loading:
            for unload in unloading:
                summ_loading_unloading = load.loading_time + unload.unloading_time
                coast_loading_unloading = load.loading_time * 1000 + unload.unloading_time * 500
                for distance in distance_route:
                    coast_distance = coast_distance + distance.distance * 50
                return summ_loading_unloading, coast_loading_unloading, coast_distance

