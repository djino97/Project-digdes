"""
Query module is designed to retrieve data from the database using queries to it.
"""

from sqlalchemy import create_engine
from models import (NextPoint, Point, Supply, Warehouse,
                    Truck, PartyCargo, Consumption, Route, Loading, Unloading)
from sqlalchemy.orm import Session
from project.math import truck_supply, truck_consumption

def build_engine():
    engine = create_engine('sqlite:///C:/PycharmProjects/progectdigdes/project/database/Logistics.db')
    session = Session(bind=engine)
    return session


def go_next_points(session):
    query_next_points = session.query(NextPoint.id_point, NextPoint.id_next_point, NextPoint.distance).all()
    return query_next_points


def go_points(session):
    query_points = session.query(Point.id_point, Point.name_point).all()
    return query_points


def go_warehouse(session):
    query_warehouse = session.query(Warehouse.id_point).all()
    return query_warehouse


def go_truck(session, weight_party):
    party = PartyCargo(weight_party=weight_party)
    session.add(party)
    id_truck_supply = session.query(Supply.truck_id_supply).all()
    truck = session.query(Truck.num_truck).filter(Truck.tonnage >= weight_party).all()
    return truck, id_truck_supply


def go_supply(session, point, weight, date, loading, num_truck):
    check_truck = 0
    query_points = session.query(Point.id_point).filter(Point.name_point == point).all()
    session.add(Loading(loading_time=loading))
    id_loading_get = session.query(Loading.id_loading).filter(Loading.loading_time == loading)
    num_party = session.query(PartyCargo).filter(PartyCargo.weight_party == weight)
    for loading in id_loading_get:
        for point in query_points:
            for party in num_party:
                if check_truck != num_truck:
                    supply = Supply(id_point=point.id_point, num_party=party.num_party, num_truck_departure=num_truck,
                                    data_departure=date, id_loading=loading.id_loading)
                    session.add(supply)
                    check_truck = num_truck
    return query_points, num_party


def delete_all(session):
    session.query(PartyCargo).delete()
    session.query(Supply).delete()
    session.query(Consumption).delete()
    session.query(Route).delete()
    session.query(Loading).delete()
    session.query(Unloading).delete()


def add_position(session, position, point):
    session.query(Point).filter(Point.id_point == point.id_point).update({"pos_x_and_y": position})


def get_pos(session, point):
    pos_point = session.query(Point.pos_x_and_y).filter(Point.id_point == point.id_point)
    return pos_point


def get_num_truck(session):
    num_truck = session.query(Truck.num_truck).all()
    truck_arrival = session.query(Supply.num_truck_departure).all()

    return num_truck, truck_arrival


def add_consumption(session, consumption, date, unloading, party, truck_arrival):
    query_points = session.query(Point.id_point).filter(Point.name_point == consumption).all()
    session.add(Unloading(unloading_time=unloading))
    id_loading_get = session.query(Loading.id_loading).filter(Loading.loading_time == unloading)
    for loading in id_loading_get:
        for point in query_points:
            for num_party in party:
                session.add(Consumption(num_party=num_party.num_party, num_truck_arrival=truck_arrival,
                                        id_point=point.num_point, data_supply=date, id_unloading=unloading))


def session_clear_field():
    session = build_engine()
    try:
        delete_all(session)
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


def session_get_pos(point):
    session = build_engine()
    try:
        pos_point = get_pos(session, point)
        session.commit()
    except:
        session.rollback()
        raise
    return pos_point


def session_add_pos(position, point):
    session = build_engine()
    try:
        add_position(session, position, point)
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


def session_create():
    session = build_engine()
    try:
        next_points = go_next_points(session)
        points = go_points(session)
        warehouse_point = go_warehouse(session)
        session.commit()
    except:
        session.rollback()
        raise

    return [next_points, points, warehouse_point]


def session_create2(**kwargs):
    session = build_engine()
    try:
        num_truck, supply_truck = go_truck(session, kwargs['weight'])
        session.commit()
        empty_truck = truck_supply(num_truck, supply_truck)
        id_supply, num_party = go_supply(session, kwargs['supply'], kwargs['weight'],
                              kwargs['date'], kwargs['loading'], empty_truck)
        session.commit()
    except:
        session.rollback()
        raise
    return [id_supply, num_party]

def session_add_consumption(**kwargs):
    session = build_engine()
    try:
        num_truck, num_truck_supply = get_num_truck(session)
        truck_arrival = truck_consumption(num_truck, num_truck_supply)
        add_consumption(session, kwargs['consumption'], kwargs['date'], kwargs['unloading'],kwargs['party'], truck_arrival)
        session.commit()
    except:
        session.rollback()

