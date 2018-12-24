"""
Query module is designed to retrieve data from the database using queries to it.
"""

from sqlalchemy import create_engine
from models import (NextPoint, Point, Supply, Warehouse,
                    Truck, PartyCargo, Consumption, Route, Loading, Unloading)
from sqlalchemy.orm import Session
from project.math import truck_supply, truck_consumption, \
    matching_supply_num_party, equality_loading, equality_unloading


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
    id_truck_supply = session.query(Supply.num_truck_departure).all()
    truck = session.query(Truck.num_truck).filter(Truck.tonnage >= weight_party).all()
    return truck, id_truck_supply


def go_supply(session, point, weight, date, loading, num_truck):
    check_truck = 0
    query_points = session.query(Point.id_point).filter(Point.name_point == point).all()
    id_loading_get = session.query(Loading).filter(Loading.loading_time == loading).all()
    if not equality_loading(id_loading_get, loading):
        session.add(Loading(loading_time=loading))
        id_loading_get = session.query(Loading).filter(Loading.loading_time == loading).all()
    num_party = session.query(PartyCargo.num_party).filter(PartyCargo.weight_party == weight).all()
    num_party_supply = session.query(Supply.num_party).all()
    num_party_matching = matching_supply_num_party(num_party, num_party_supply)
    for loading in id_loading_get:
        for point in query_points:
                if check_truck != num_truck:
                    supply = Supply(id_point=point.id_point, num_party=num_party_matching, num_truck_departure=num_truck,
                                    date_departure=date, id_loading=loading.id_loading)
                    session.add(supply)
                    check_truck = num_truck
    return query_points, num_party_matching


def delete_all(session):
    session.query(Supply).delete()
    session.query(Consumption).delete()
    session.query(Route).delete()
    session.query(PartyCargo).delete()
    session.query(Loading).delete()
    session.query(Unloading).delete()


def add_position(session, position, point):
    session.query(Point).filter(Point.id_point == point.id_point).update({"pos_x_and_y": position})


def get_pos(session, point):
    pos_point = session.query(Point.pos_x_and_y).filter(Point.id_point == point.id_point)
    return pos_point


def get_num_truck(session, num_party):
    num_truck = session.query(Truck.num_truck).all()
    truck_supply_departure = session.query(Supply.num_truck_departure).filter(Supply.num_party == num_party).all()
    truck_consumption_arrival = session.query(Consumption.num_truck_arrival).all()
    return [num_truck, truck_supply_departure, truck_consumption_arrival]


def add_consumption(session, consumption, date, unloading, party, truck_arrival):
    query_points = session.query(Point.id_point).filter(Point.name_point == consumption).all()
    id_unloading_get = session.query(Unloading).filter(Unloading.unloading_time == unloading).all()
    if not equality_unloading(id_unloading_get, unloading):
        session.add(Unloading(unloading_time=unloading))
        id_unloading_get = session.query(Unloading).filter(Unloading.unloading_time == unloading).all()
    for unloading in id_unloading_get:
        for point in query_points:
                session.add(Consumption(num_party=party, num_truck_arrival=truck_arrival,
                                        id_point=point.id_point, date_supply=date, id_unloading=unloading.id_unloading))
        return query_points


def add_route(session, lst_point, route, id_supply, empty_truck):
    for lst in lst_point:
        next_point = session.query(NextPoint).filter(NextPoint.id_point == lst[0],
                                                     NextPoint.id_next_point == lst[1]).all()
        for agent in next_point:
            for supply in id_supply:
                get_num_party = session.query(Supply.num_party).filter(Supply.id_point == supply.id_point,
                                                                       Supply.num_truck_departure == empty_truck)
                for party in get_num_party:
                    session.add(Route(id_agent=agent.id_agent, distance=agent.distance, num_route=int(route),
                                      num_party=party.num_party))


def get_routs(session):
    routs = session.query(Route).all()
    return routs


def get_agents(session, id_agent):
    agents = session.query(NextPoint.id_point, NextPoint.id_next_point).filter(NextPoint.id_agent == id_agent)
    return agents


def get_supply_consumption(session, num_party):
    supply = session.query(Supply.id_point).filter(Supply.num_party == num_party)
    consumption = session.query(Consumption.id_point).filter(Supply.num_party == num_party)
    return supply, consumption


def get_pos_point(session, id_point, id_next_point):
    pos_point = session.query(Point.pos_x_and_y).filter(Point.id_point == id_point)
    pos_next_point = session.query(Point.pos_x_and_y).filter(Point.id_point == id_next_point)
    return pos_point, pos_next_point


def get_loading_unloading(session, route):
    loading = []
    unloading = []
    num_party_supply = session.query(Supply).join(Route, Route.num_party == Supply.num_party).\
                                                 filter(Route.num_route == route).all()
    num_party_consumption = session.query(Consumption).join(Route, Route.num_party == Consumption.num_party).\
                                                            filter(Route.num_route == route).all()
    for time_supply in num_party_supply:
        loading = session.query(Loading.loading_time).filter(Loading.id_loading == time_supply.id_loading)
    for time_consumption in num_party_consumption:
        unloading = session.query(Unloading.unloading_time).filter(Unloading.id_unloading == time_consumption.id_unloading)
    distance_route = session.query(Route).filter(Route.num_route == route).all()
    return loading, unloading, distance_route


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
        empty_truck = truck_supply(num_truck, supply_truck)
        id_supply, num_party = go_supply(session, kwargs['supply'], kwargs['weight'],
                              kwargs['date'], kwargs['loading'], empty_truck)
        session.commit()
    except:
        session.rollback()
        raise
    return [id_supply, num_party, empty_truck]


def session_add_consumption(**kwargs):
    session = build_engine()
    try:
        num_truck, num_truck_supply, num_truck_consumption = get_num_truck(session, kwargs['party'])
        truck_arrival = truck_consumption(num_truck, num_truck_supply, kwargs['travel_time'], num_truck_consumption)
        id_consumption = add_consumption(session, kwargs['consumption'], kwargs['date'],
                                         kwargs['unloading'], kwargs['party'], truck_arrival)
        session.commit()
    except:
        session.rollback()
        raise
    return id_consumption, truck_arrival


def session_add_route(lst_point, route, id_supply, empty_truck):
    session = build_engine()
    try:
        add_route(session, lst_point, route, id_supply, empty_truck)
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close_all()


def session_get_routs():
    session = build_engine()
    try:
        routs = get_routs(session)
        session.commit()
    except:
        session.rollback()
        raise
    return routs


def session_get_agents(id_agent):
    session = build_engine()
    try:
        agents = get_agents(session, id_agent)
        session.commit()
    except:
        session.rollback()
        raise
    return agents


def get_id_supply_consumption(num_party):
    session = build_engine()
    try:
        supply_consumption = get_supply_consumption(session, num_party)
        session.commit()
    except:
        session.rollback()
        raise
    return supply_consumption


def session_get_pos_point(id_point, id_next_point):
    session = build_engine()
    try:
        pos_point, pos_next_point = get_pos_point(session, id_point, id_next_point)
        session.commit()
    except:
        session.rollback()
        raise
    return pos_point, pos_next_point


def session_get_loading_unloading(route):
    session = build_engine()
    try:
        loading, unloading, distance_route = get_loading_unloading(session, route)
        session.commit()
    except:
        session.rollback()
        raise
    return loading, unloading, distance_route

