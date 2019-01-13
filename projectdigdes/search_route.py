from database.query import session_getting_route,\
    get_id_supply_consumption, session_get_name_point


def list_routs():
    """
    The function sends a string
    of all routes to the main window
    :return: string of routes that exist in the Route table
    """
    routs, session = session_getting_route()
    str_route = 'Маршруты:'
    check = 0
    for route in routs:
        if route.num_party != check:
            supply, consumption = get_id_supply_consumption(route.num_party)
            check = route.num_party
            point = []
            for s in supply:
                for c in consumption:
                    point = session_get_name_point(s.id_point, c.id_point)
            lst_point = []
            for name_point in point:
                lst_point.append(name_point.name_point)
            str_route = str_route + '№{0}:{1} - {2};\t'.format(route.num_route, lst_point[0], lst_point[1])
    session.close_all()
    return str_route, check

