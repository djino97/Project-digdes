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


def truck_supply(truck, truck_work):
    """
    Calculating unoccupied(not busy) truck number
    :param truck: all truck
    :param truck_work: truck busy
    :return:truck not busy
    """
    for truck_1 in truck:
        if truck_work:
            for truck_2 in truck_work:
                if truck_1.num_truck > truck_2.num_truck_departure:
                    return truck_1.num_truck
                else:
                    break
        else:
            return truck_1.num_truck


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


def truck_consumption(num_truck, num_truck_supply, travel_time, num_truck_consumption):
    """
    If the difference between the date of departure
    and the arrival is more than 1 day, then calculating unoccupied(not busy) truck number
    :param num_truck: all number truck
    :param num_truck_supply: all number truck supply
    :param travel_time:difference between the date of departure and the arrival
    :param num_truck_consumption: all number truck consumption
    :return: truck not busy
    """
    for num_truck_b in num_truck:
        if travel_time > 1:
                for num_truck_c in num_truck_consumption:
                    for num_truck_s in num_truck_supply:
                        if num_truck_s.num_truck_departure != num_truck_b.num_truck and \
                             num_truck_s.num_truck_departure != num_truck_c.num_truck_arrival and \
                                num_truck_b.num_truck != num_truck_c.num_truck_arrival:
                                return num_truck_b.num_truck
                        else:
                            break
                return num_truck_b.num_truck

        else:
            for num_truck_s in num_truck_supply:
                num_truck = num_truck_s.num_truck_departure
                return num_truck


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











