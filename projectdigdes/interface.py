from PyQt5.QtWidgets import (QWidget, QLabel, QComboBox)
from PyQt5 import QtCore
from query import session_create, session_create2, session_add_consumption, session_clear_field
from PyQt5.QtWidgets import QPushButton, QDateTimeEdit, QHBoxLayout, QVBoxLayout
from buildgraph import update_graphic
from project.math import loading_party, unloading_party
import datetime


def point(id_point, warehouse):
    """
    A list of all the points not including warehouses
    use the symmetric difference
    :param id_point: a list of all points
    :param warehouse: a list of all warehouse
    :return lst_name_point: the list excludes points of warehouses
    """

    lst_id_point = []
    lst_id_warehouse = []
    for val in id_point:
        lst_id_point.append(val.id_point)
    for id_warehouse in warehouse:
        lst_id_warehouse.append(id_warehouse.id_point)
    result = list(set(lst_id_point) ^ set(lst_id_warehouse))
    lst_name_point = []
    for elem in result:
        for p in id_point:
            if elem == p.id_point:
                lst_name_point.append(p.name_point)
    return lst_name_point


def parsing_tuple():
    """
    From method session_create selected tuples
    tuple[1] = point; tuple[2] = warehouse
    :return: result point
    """

    tuple = session_create()
    return point(tuple[1], tuple[2])


class Example(QWidget):
    trigger = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent, QtCore.Qt.Window)

        self.combo_route = QComboBox(self)
        self.combo_route.addItems(['1', '2'])
        self.combo_route.move(150, 120)
        self.combo_route.resize(self.combo_route.sizeHint())

        """
        Data entry for supply
        """
        pars = parsing_tuple()
        self.combo_supply = QComboBox(self)
        self.combo_supply.addItems(pars)

        self.combo_weight_party = QComboBox(self)
        self.combo_weight_party.addItems(['20', '30', '40'])
        self.date_supply = QDateTimeEdit()

        vbox = QVBoxLayout()
        layout = QHBoxLayout(self)
        layout.addLayout(vbox)
        layout.addWidget(self.combo_supply)
        layout.addWidget(self.combo_weight_party)
        layout.addWidget(self.date_supply)
        layout.addStretch(1)

        """
        Data entry for consumption
        """
        self.combo_consumption = QComboBox(self)
        self.combo_consumption.addItems(pars)
        self.date_consumption = QDateTimeEdit()

        layout.addWidget(self.combo_consumption)
        layout.addWidget(self.date_consumption)

        self.initUI()

    def initUI(self):
        btn_input = QPushButton('Ввести значения', self)
        btn_input.resize(btn_input.sizeHint())
        btn_input.move(420, 120)
        btn_input.clicked.connect(self.get_supply_consumption)

        btn_delete_route = QPushButton('Удалить маршруты', self)
        btn_delete_route.resize(btn_delete_route.sizeHint())
        btn_delete_route.move(310, 120)
        btn_delete_route.clicked.connect(self.delete_route)

        lbl_route = QLabel("Маршрут:", self)
        lbl_route.resize(lbl_route.sizeHint())
        lbl_route.move(100, 120)

        lbl_supply = QLabel("Точка поставки", self)
        lbl_supply.move(100, 10)

        lbl_consupmtion = QLabel("Точка потребления", self)
        lbl_consupmtion.move(450, 10)

        lbl_supply_point = QLabel("Пункт", self)
        lbl_supply_point.move(40, 35)

        lbl_weight_party = QLabel("Вес партии", self)
        lbl_weight_party.move(105, 35)

        lbl_date_departure = QLabel("Дата отправления", self)
        lbl_date_departure.move(170, 35)

        lbl_consumption_point = QLabel("Пункт", self)
        lbl_consumption_point.move(415, 35)

        lbl_date_arrival = QLabel("Дата прибытия", self)
        lbl_date_arrival.move(495, 35)

        self.setGeometry(300, 300, 600, 150)
        self.setWindowTitle('Выбрать параметры поставки груза')

    def delete_route(self):
        """
        delete data before use program
        :return: nothing
        """
        session_clear_field()
        self.trigger.emit()

    def get_supply_consumption(self):
        """
        Data collection from forms
        :return: nothing
        """
        supply = self.combo_supply.currentText()
        consumption = self.combo_consumption.currentText()
        route = self.combo_route.currentText()
        date_arrival = datetime.datetime(int(self.date_consumption.dateTime().toString("yyyy")),
                                         int(self.date_consumption.dateTime().toString("MM")),
                                         int(self.date_consumption.dateTime().toString("dd")),
                                         int(self.date_consumption.dateTime().toString("hh")))
        date_departure = datetime.datetime(int(self.date_supply.dateTime().toString("yyyy")),
                                           int(self.date_supply.dateTime().toString("MM")),
                                           int(self.date_supply.dateTime().toString("dd")),
                                           int(self.date_supply.dateTime().toString("hh")))
        weight = int(self.combo_weight_party.currentText())
        loading = loading_party(weight)
        id_supply, num_party, empty_truck = session_create2(weight=weight, supply=supply, date=date_departure, loading=loading)
        unloading = unloading_party(weight)
        travel_time = date_arrival - date_departure
        id_consumption,  truck_arrival = session_add_consumption(consumption=consumption, date=date_arrival, unloading=unloading,
                                                                 party=num_party, travel_time=travel_time.days)
        update_graphic(id_supply, id_consumption, route, empty_truck)
        self.trigger.emit()



