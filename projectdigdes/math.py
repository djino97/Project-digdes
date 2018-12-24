

def loading_party(weight):
    loading = weight // 2
    return loading


def unloading_party(weight):
    unloading = weight // 4
    return unloading


def truck_supply(truck, truck_work):

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
    for party in num_party:
        if num_party_supply:
            for party_supply in num_party_supply:
                if party.num_party != party_supply.num_party:
                    return party.num_party
        else:
            return party.num_party


def truck_consumption(num_truck, num_truck_supply, travel_time, num_truck_consumption):

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
            return num_truck_b.num_truck


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


