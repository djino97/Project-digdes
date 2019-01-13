from PyQt5.QtWidgets import (QWidget, QLabel, QComboBox, QPushButton)
from PyQt5 import QtCore
from database.query import session_get_data_route


class MathRoute(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent, QtCore.Qt.Window)
        self.sum_loading_unloading = 0
        self.coast_loading_unloading = 0
        self.coast_distance = 0
        self.combo_route = QComboBox(self)
        self.combo_route.addItems(['1', '2', '3'])
        self.combo_route.move(160, 25)

        self.lbl_supply = QLabel("Суммарное время разгрузки и погрузки партии: {0} часов, "
                                 "расчетная стоимость: {1} ₽".format(self.sum_loading_unloading,
                                                                  self.coast_loading_unloading), self)

        self.lbl_coast_distance = QLabel("Расчет суммы за каждый пройденный километр: {0} ₽"
                                         .format(self.coast_distance), self)
        self.initUI()

    def initUI(self):
        lbl_route = QLabel("Выбрать маршрут", self)
        lbl_route.move(60, 25)

        self.combo_route.activated[str].connect(self.math_route)

        self.lbl_supply.move(60, 50)
        self.lbl_coast_distance.move(60, 70)

        self.setGeometry(300, 300, 550, 150)
        self.setWindowTitle('Расчет маршрута')

    def math_route(self, text):
        loading, unloading, distance_route = session_get_data_route(int(text))
        for load in loading:
            for unload in unloading:
                self.sum_loading_unloading = load.loading_time + unload.unloading_time
                self.coast_loading_unloading = load.loading_time * 1000 + unload.unloading_time * 500
                for distance in distance_route:
                    self.coast_distance += distance.distance * 50
        self.lbl_supply.setText("Суммарное время разгрузки и погрузки партии: {0} часов, "
                                "расчетная стоимость: {1} ₽".format(self.sum_loading_unloading,
                                                                  self.coast_loading_unloading))
        self.lbl_supply.adjustSize()
        self.lbl_coast_distance.setText("Расчет суммы за каждый пройденный километр: {0} ₽"
                                        .format(self.coast_distance))
        self.lbl_coast_distance.adjustSize()
