"""
Query module is designed to retrieve data from the database using queries to it.
"""

from sqlalchemy import create_engine, or_
from models import (NextPoint, Point, Supply, Warehouse,
                    Truck, PartyCargo, Consumption, Route, Loading, Unloading)
from sqlalchemy.orm import Session
from project.math import truck_supply, truck_consumption, \
    matching_supply_num_party, equality_loading, equality_unloading


def build_engine():
    """
    Creating an engine and session
    :return: bind session
    """
    engine = create_engine('sqlite:///C:/PycharmProjects/progectdigdes/project/database/Logistics.db',
                           connect_args={'check_same_thread': False}, echo=True)
    session = Session(bind=engine)
    return session


def go_next_points(session):
    """
    Getting all agents
    id_point -  starting point
    id_next_point - end point
    distance - distance from start to end
    :param session:
    :return:query_next_points
    """
    query_next_points = session.query(NextPoint.id_point, NextPoint.id_next_point, NextPoint.distance).all()
    return query_next_points


def go_points(session):
    """
    Getting all tuple from table Point
    :param session:
    :return: query_points
    """
    query_points = session.query(Point.id_point, Point.name_point).all()
    return query_points


def go_warehouse(session):
    """
    Getting all id Warehouse
    :param session:
    :return: query_warehouse
    """
    query_warehouse = session.query(Warehouse.id_point).all()
    return query_warehouse


def go_truck(session, weight_party):
    """
    Add new party in the table PartyCargo and
    selection tonnage truck appropriate weight party
    :param session:
    :param weight_party:
    :return:truck, id_truck_supply
    """
    party = PartyCargo(weight_party=weight_party)
    session.add(party)
    id_truck_supply = session.query(Supply.num_truck_departure).all()
    truck = session.query(Truck.num_truck).filter(Truck.tonnage >= weight_party).all()
    return truck, id_truck_supply


def go_supply(session, point, weight, date, loading, num_truck):
    """
    Add supply appropriate this party and number truck
    :param session:
    :param point:
    :param weight:
    :param date: date departure from supply
    :param loading:load time party in the truck
    :param num_truck:
    :return:query_points, num_party_matching
    """
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
    """
    Delete all data from database before use program
    :param session:
    :return:nothing
    """
    session.query(Supply).delete()
    session.query(Consumption).delete()
    session.query(Route).delete()
    session.query(PartyCargo).delete()
    query_warehouse = session.query(Warehouse.id_loading, Warehouse.id_unloading).all()
    for query in query_warehouse:
        session.query(Loading).filter(Loading.id_loading != query.id_loading).delete()
        session.query(Unloading).filter(Unloading.id_unloading != query.id_unloading).delete()

def add_position(session, position, point):
    """
    Add position x and y preassigned point in the table Point
    :param session:
    :param position:
    :param point:
    :return:nothing
    """
    session.query(Point).filter(Point.id_point == point.id_point).update({"pos_x_and_y": position})


def get_pos(session, point):
    """
    Getting position x and y preassigned point
    :param session:
    :param point:
    :return: pos_point - position x and y point
    """
    pos_point = session.query(Point.pos_x_and_y).filter(Point.id_point == point.id_point)
    return pos_point


def get_num_truck(session, num_party):
    """
    Getting number truck, truck supply departure, truck consumption arrival
    :param session:
    :param num_party:
    :return: number truck, truck supply departure, truck consumption arrival
    """
    num_truck = session.query(Truck.num_truck).all()
    truck_supply_departure = session.query(Supply.num_truck_departure).filter(Supply.num_party == num_party).all()
    truck_consumption_arrival = session.query(Consumption.num_truck_arrival).all()
    return [num_truck, truck_supply_departure, truck_consumption_arrival]


def add_consumption(session, consumption, date, unloading, party, truck_arrival):
    """
    Add consumption in the table Consumption
    :param session:
    :param consumption:
    :param date:
    :param unloading:unload time party from truck
    :param party:
    :param truck_arrival:
    :return:query_points - getting all points
    """
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
    """
    Add route for each party
    :param session:
    :param lst_point:
    :param route:
    :param id_supply:
    :param empty_truck:
    :return:nothing
    """
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
    """
    Getting all route
    :param session:
    :return: tuple all routs
    """
    routs = session.query(Route).all()
    return routs


def get_agents(session, id_agent):
    """
    Getting id start point and id end point for given id agent
    :param session:
    :param id_agent:
    :return: id start point and id end point
    """
    agents = session.query(NextPoint.id_point, NextPoint.id_next_point).filter(NextPoint.id_agent == id_agent)
    return agents


def get_supply_consumption(session, num_party):
    """
    Getting supply and consumption for given number party
    :param session:
    :param num_party:
    :return: supply, consumption
    """
    supply = session.query(Supply.id_point).filter(Supply.num_party == num_party)
    consumption = session.query(Consumption.id_point).filter(Consumption.num_party == num_party)
    return supply, consumption


def get_pos_point(session, id_point, id_next_point):
    """
    Getting position start and end point
    :param session:
    :param id_point:
    :param id_next_point:
    :return: pos_point, pos_next_point
    """
    pos_point = session.query(Point.pos_x_and_y).filter(Point.id_point == id_point)
    pos_next_point = session.query(Point.pos_x_and_y).filter(Point.id_point == id_next_point)
    return pos_point, pos_next_point


def get_data_route(session, route):
    """
    Getting loading and unloading time party for calculations cost
    Getting all distance route for calculations cost
    :param session:
    :param route:
    :return: loading and unloading time party, distance route
    """
    loading = []
    unloading = []
    num_party_supply = session.query(Supply).join(Route, Route.num_party == Supply.num_party).\
        filter(Route.num_route == route).all()
    num_party_consumption = session.query(Consumption).join(Route, Route.num_party == Consumption.num_party).\
        filter(Route.num_route == route).all()
    for time_supply in num_party_supply:
        loading = session.query(Loading.loading_time).filter(Loading.id_loading == time_supply.id_loading)
    for time_consumption in num_party_consumption:
        unloading = session.query(Unloading.unloading_time).\
            filter(Unloading.id_unloading == time_consumption.id_unloading)
    distance_route = session.query(Route).filter(Route.num_route == route).all()
    return loading, unloading, distance_route


def get_name_point(session, supply, consumption):
    name_point = session.query(Point.name_point).\
        filter(or_(Point.id_point == supply, Point.id_point == consumption)).all()
    return name_point


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
        supply, consumption = get_supply_consumption(session, num_party)
        session.commit()
    except:
        session.rollback()
        raise
    return supply, consumption


def session_get_pos_point(id_point, id_next_point):
    session = build_engine()
    try:
        pos_point, pos_next_point = get_pos_point(session, id_point, id_next_point)
        session.commit()
    except:
        session.rollback()
        raise
    return pos_point, pos_next_point


def session_get_data_route(route):
    session = build_engine()
    try:
        loading, unloading, distance_route = get_data_route(session, route)
        session.commit()
    except:
        session.rollback()
        raise
    return loading, unloading, distance_route


def session_get_name_point(supply, consumption):
    session = build_engine()
    try:
        name_point = get_name_point(session, supply, consumption)
        session.commit()
    except:
        session.rollback()
        raise
    return name_point


def session_getting_route():
    session = build_engine()
    try:
        route = session.query(Route).all()
    except:
        session.rollback()
        raise
    return route, session
