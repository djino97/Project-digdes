"""
Query module is designed to retrieve data from the database using queries to it.
"""

from models import *
from sqlalchemy.orm import Session
from project.math import matching_supply_num_party, equality_loading,\
    equality_unloading, search_date


def build_engine():
    """
    Creating an engine and session
    :return: bind session
    """
    engine = create_engine('sqlite:///C:/PycharmProjects/progectdigdes/project/database/Logistics.db',
                           connect_args={'check_same_thread': False})
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
    empty_truck = session.query(Truck). \
        outerjoin(Consumption, Truck.num_truck == Consumption.num_truck_arrival). \
        outerjoin(Supply, Truck.num_truck == Supply.num_truck_departure). \
        filter(and_(Consumption.num_truck_arrival == None, Supply.num_truck_departure == None,
                    Truck.tonnage >= weight_party))
    for truck in empty_truck:
        return truck.num_truck


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
            supply = Supply(id_point=point.id_point, num_party=num_party_matching,
                            num_truck_departure=num_truck, date_departure=date, id_loading=loading.id_loading)
            session.add(supply)
    return query_points, num_party_matching


def delete_all(session):
    """
    Delete all data from database before use program
    :param session:
    :return:nothing
    """
    session.query(Supply).delete()
    session.query(Consumption).delete()
    session.query(WarehouseParty).delete()
    session.query(Route).delete()
    session.query(PartyCargo).delete()
    session.query(Loading).delete()
    session.query(Unloading).delete()


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
                                        id_point=point.id_point, date_arrival=date, id_unloading=unloading.id_unloading))
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
    count_point_route = 0
    for lst in lst_point:
        next_point = session.query(NextPoint).filter(NextPoint.id_point == lst[0],
                                                     NextPoint.id_next_point == lst[1]).all()
        for agent in next_point:
            for supply in id_supply:
                get_num_party = session.query(Supply.num_party).filter(Supply.id_point == supply.id_point,
                                                                       Supply.num_truck_departure == empty_truck)
                for party in get_num_party:
                    count_point_route += 1
                    session.add(Route(id_agent=agent.id_agent, distance=agent.distance, num_route=int(route),
                                      num_party=party.num_party, num_point_route=count_point_route))


def get_routs(session, date_supply, count_agent):
    """
    Getting route at number party
    :param session:
    :param count_agent:
    :param date_supply:
    :return: tuple all routs
    """
    num_party = session.query(Supply.num_party).filter(Supply.date_departure == date_supply)
    lst = []
    for party in num_party:
        lst.append(party.num_party)
    if count_agent != 1:
        warehouse_party = []
        warehouse = session.query(WarehouseParty.num_party).filter(WarehouseParty.date_departure == date_supply)
        for w in warehouse:
            warehouse_party.append(w.num_party)
        if warehouse_party:
            num_point_route = session.query(func.max(Route.num_point_route)).filter(Route.num_party.in_(warehouse_party))
            routs = session.query(Route).filter(and_(Route.num_party.in_(warehouse_party), Route.num_point_route == num_point_route))
        else:
            routs = session.query(Route).filter(and_(Route.num_party.in_(lst), Route.num_point_route == count_agent))
    else:
        routs = session.query(Route).filter(and_(Route.num_party.in_(lst), Route.num_point_route == count_agent))
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
        supply_truck = session.query(Supply.id_point).all()
        pos_point = get_pos(session, point)
        session.commit()
    except:
        session.rollback()
        raise
    return pos_point, supply_truck


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
        truck_departure = go_truck(session, kwargs['weight'])
        id_supply, num_party = go_supply(session, kwargs['supply'], kwargs['weight'],
                                         kwargs['date'], kwargs['loading'], truck_departure)
        session.commit()
    except:
        session.rollback()
        raise
    return [id_supply, num_party, truck_departure]


def session_add_consumption(**kwargs):
    session = build_engine()
    try:

        if kwargs['travel_time'] > 1:
            truck_arrival = session.query(Truck.num_truck). \
                outerjoin(Consumption, Truck.num_truck == Consumption.num_truck_arrival). \
                outerjoin(Supply, Truck.num_truck == Supply.num_truck_departure). \
                filter(and_(Consumption.num_truck_arrival == None, Supply.num_truck_departure == None,
                            Truck.tonnage >= kwargs['weight']))
        else:
            truck_arrival = session.query(Supply.num_truck_departure)\
                .filter(Supply.num_party == kwargs['party'])
        for truck in truck_arrival:
            truck_arrival = truck[0]
            break
        id_consumption = add_consumption(session, kwargs['consumption'], kwargs['date'],
                                         kwargs['unloading'], kwargs['party'], truck_arrival)
        session.commit()
    except Exception as e:
        session.rollback()
        print(e)
        raise
    return id_consumption


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


def session_get_routs(date_supply, count_agent):
    session = build_engine()
    try:
        routs = get_routs(session, date_supply, count_agent)
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
        session.commit()
    except:
        session.rollback()
        raise
    return route, session


def session_add_warehouse(warehouse):
    session = build_engine()
    try:
        id_point = session.query(Point.id_point).filter(Point.name_point == warehouse)
        for point in id_point:
            session.add(Warehouse(id_point=point.id_point))
        session.commit()
    except:
        session.rollback()
        raise


def session_get_warehouse():
    session = build_engine()
    try:
        warehouse = session.query(Point).join(Warehouse, Point.id_point == Warehouse.id_point).all()
        session.commit()
    except:
        session.rollback()
        raise
    return warehouse


def session_delete_warehouse():
    session = build_engine()
    try:
        session.query(Warehouse).delete()
        session.commit()
    except:
        session.rollback()
        raise


def session_getting_warehouse():
    session = build_engine()
    try:
        warehouse_point = go_warehouse(session)
        session.commit()
    except:
        session.rollback()
        raise
    return warehouse_point


def session_add_warehouse_party(route_points, warehouse_point, num_party, loading, unloading):
    session = build_engine()
    try:
        id_loading = session.query(Loading.id_loading).filter(Loading.loading_time == loading)
        id_unloading = session.query(Unloading.id_unloading).filter(Unloading.unloading_time == unloading)
        supply_date = session.query(Supply.date_departure).filter(Supply.num_party == num_party)
        consumption_date = session.query(Consumption.date_arrival).filter(Consumption.num_party == num_party)
        date_arrival, date_departure = search_date(supply_date, consumption_date, route_points, warehouse_point)

        for load in id_loading:
            for unload in id_unloading:
                session.add(WarehouseParty(id_point=warehouse_point, num_party=num_party,
                                           id_loading=load.id_loading, id_unloading=unload.id_unloading,
                                           date_arrival=date_arrival, date_departure=date_departure))
        session.commit()
    except:
        session.rollback()
        raise


def session_get_next_point():
    session = build_engine()
    try:
        next_point = go_next_points(session)
        session.commit()
    except:
        session.rollback()
        raise
    return next_point


def session_route():
    session = build_engine()
    try:
        max_route = session.query(func.max(Route.num_route))
        all_optimal_point = []
        for m in max_route:
            count_route = 0
            while count_route != m[0]:
                count_route += 1
                next_point = session.query(NextPoint.id_point, NextPoint.id_next_point).\
                    join(Route, Route.id_agent == NextPoint.id_agent).filter(Route.num_route == count_route).\
                    order_by(Route.num_point_route)
                optimal_point = []
                for point in next_point:
                    optimal_point.append(point.id_point)
                    optimal_point.append(point.id_next_point)
                    all_optimal_point.append(optimal_point)
                    optimal_point = []
        session.commit()
    except:
        session.rollback()
        raise
    return all_optimal_point


def session_get_date():
    session = build_engine()
    try:
        min_date_supply = session.query(func.min(Supply.date_departure))
        max_date_supply = session.query(func.max(Consumption.date_arrival))
        session.commit()
    except:
        session.rollback()
        raise
    return min_date_supply, max_date_supply
