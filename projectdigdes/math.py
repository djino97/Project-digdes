from datetime import timedelta


def loading_party(weight):
    """
    Calculation of time for loading party
    :param weight: weight party
    :return: loading time
    """
    loading = weight // 2
    return loading


def unloading_party(weight):
    """
    Calculation of time for unloading party
    :param weight: weight party
    :return: unloading time
    """
    unloading = weight // 4
    return unloading


def matching_supply_num_party(num_party, num_party_supply):
    """
    Check conformity supply and number party
    :param num_party:
    :param num_party_supply:
    :return:conformity supply and number party
    """
    for party in num_party:
        if num_party_supply:
            for party_supply in num_party_supply:
                if party.num_party != party_supply.num_party:
                    return party.num_party
        else:
            return party.num_party


def equality_loading(id__get_loading, loading):
    for id_loading in id__get_loading:
        if id_loading.loading_time == loading:
            return True
    return False


def equality_unloading(id__get_unloading, unloading):
    for id_unloading in id__get_unloading:
        if id_unloading.unloading_time == unloading:
            return True
    return False


def search_date(supply, consumption, route_points, warehouse_point):
    days_before_warehouse = 0
    day = 0
    for day, route_point in enumerate(route_points):
        if route_point == warehouse_point:
            days_before_warehouse = day
    else:
        days_after_warehouse = day - days_before_warehouse
    for s in supply:
        for c in consumption:
            warehouse_arrival = s.date_departure + timedelta(days=days_before_warehouse)
            warehouse_departure = c.date_arrival - timedelta(days=days_after_warehouse)
            return warehouse_arrival, warehouse_departure







