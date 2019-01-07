from PyQt5.QtWidgets import (QWidget, QLabel, QComboBox)
from PyQt5 import QtCore
from query import session_create, session_create2, \
    session_add_consumption, session_clear_field, \
    session_add_warehouse, session_get_warehouse, session_delete_warehouse
from PyQt5.QtWidgets import QPushButton, QDateTimeEdit,\
    QHBoxLayout, QVBoxLayout, QFrame
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

        self.top_warehouse = QFrame(self)
        self.top_warehouse.setFrameShape(QFrame.StyledPanel)
        self.top_warehouse.resize(584, 75)
        self.top_warehouse.move(8, 10)

        self.top_route = QFrame(self)
        self.top_route.setFrameShape(QFrame.StyledPanel)
        self.top_route.resize(584, 170)
        self.top_route.move(8, 88)

        self.top_supply = QFrame(self)
        self.top_supply.setFrameShape(QFrame.StyledPanel)
        self.top_supply.resize(285, 110)
        self.top_supply.move(10, 92)

        self.top_consumption = QFrame(self)
        self.top_consumption.setFrameShape(QFrame.StyledPanel)
        self.top_consumption.resize(286, 110)
        self.top_consumption.move(304, 92)

        self.combo_route = QComboBox(self)
        self.combo_route.addItems(['1', '2'])
        self.combo_route.move(150, 220)
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
        Data entry for warehouse
        """
        self.combo_warehouse = QComboBox(self)
        self.combo_warehouse.addItems(pars)
        self.combo_warehouse.move(150, 30)
        self.combo_warehouse.resize(self.combo_warehouse.sizeHint())

        self.lbl_warehouse = QLabel("Склады", self)
        self.lbl_warehouse.move(300, 30)

        """
        Data entry for consumption
        """
        self.combo_consumption = QComboBox(self)
        self.combo_consumption.addItems(pars)
        self.date_consumption = QDateTimeEdit()

        layout.addWidget(self.combo_consumption)
        layout.addWidget(self.date_consumption)

        self.check_warehouse()
        self.initUI()

    def initUI(self):
        btn_input = QPushButton('Ввести значения', self)
        btn_input.resize(btn_input.sizeHint())
        btn_input.move(420, 220)
        btn_input.clicked.connect(self.get_supply_consumption)

        btn_delete_route = QPushButton('Удалить маршруты', self)
        btn_delete_route.resize(btn_delete_route.sizeHint())
        btn_delete_route.move(310, 220)
        btn_delete_route.clicked.connect(self.delete_route)

        btn_delete_warehouse = QPushButton('Удалить склады', self)
        btn_delete_warehouse.resize(btn_delete_warehouse.sizeHint())
        btn_delete_warehouse.move(490, 55)
        btn_delete_warehouse.clicked.connect(self.delete_warehouse)

        btn_add_warehouse = QPushButton('Добавить склад', self)
        btn_add_warehouse.resize(btn_delete_route.sizeHint())
        btn_add_warehouse.move(40, 30)
        btn_add_warehouse.clicked.connect(self.update_warehouse)

        lbl_route = QLabel("Маршрут:", self)
        lbl_route.resize(lbl_route.sizeHint())
        lbl_route.move(100, 220)

        lbl_supply = QLabel("Точка поставки", self)
        lbl_supply.resize((lbl_supply.sizeHint()))
        lbl_supply.move(90, 93)

        lbl_consupmtion = QLabel("Точка потребления", self)
        lbl_consupmtion.resize(lbl_consupmtion.sizeHint())
        lbl_consupmtion.move(450, 93)

        lbl_supply_point = QLabel("Пункт", self)
        lbl_supply_point.resize(lbl_supply_point.sizeHint())
        lbl_supply_point.move(25, 115)

        lbl_weight_party = QLabel("Вес партии", self)
        lbl_weight_party.resize(lbl_weight_party.sizeHint())
        lbl_weight_party.move(70, 115)

        lbl_date_departure = QLabel("Дата отправления", self)
        lbl_date_departure.resize(lbl_date_departure.sizeHint())
        lbl_date_departure.move(145, 115)

        lbl_consumption_point = QLabel("Пункт", self)
        lbl_consumption_point.resize(lbl_consumption_point.sizeHint())
        lbl_consumption_point.move(420, 115)

        lbl_date_arrival = QLabel("Дата прибытия", self)
        lbl_date_arrival.resize(lbl_date_arrival.sizeHint())
        lbl_date_arrival.move(490, 115)

        self.setGeometry(300, 300, 600, 300)
        self.setWindowTitle('Выбрать параметры поставки груза')

    def delete_warehouse(self):
        session_delete_warehouse()
        self.check_warehouse()
        pars = parsing_tuple()
        self.combo_warehouse.clear()
        self.combo_supply.clear()
        self.combo_consumption.clear()
        self.combo_warehouse.addItems(pars)
        self.combo_supply.addItems(pars)
        self.combo_consumption.addItems(pars)

    def delete_route(self):
        """
        delete data before use program
        :return: nothing
        """
        session_clear_field()
        self.trigger.emit()
        pars = parsing_tuple()
        self.combo_warehouse.clear()
        self.combo_supply.clear()
        self.combo_consumption.clear()
        self.combo_warehouse.addItems(pars)
        self.combo_supply.addItems(pars)
        self.combo_consumption.addItems(pars)

    def check_warehouse(self):
        str_warehouse = 'Склады:'
        name_warehouse = session_get_warehouse()
        for warehouse in name_warehouse:
            str_warehouse = str_warehouse + warehouse.name_point + ','
        self.lbl_warehouse.setText(str_warehouse)
        self.lbl_warehouse.adjustSize()

    def update_warehouse(self):
        warehouse = self.combo_warehouse.currentText()
        session_add_warehouse(warehouse)
        self.check_warehouse()
        pars = parsing_tuple()
        self.combo_warehouse.clear()
        self.combo_supply.clear()
        self.combo_consumption.clear()
        self.combo_warehouse.addItems(pars)
        self.combo_supply.addItems(pars)
        self.combo_consumption.addItems(pars)

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



