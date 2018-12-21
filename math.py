def loading_party(weight):
    loading = weight // 2
    return loading


def unloading_party(weight):
    unloading = weight // 4
    return unloading


def truck_supply(truck, truck_work):
    for truck_1 in truck:
        if not truck_work:
            for truck_2 in truck_work:
                if truck_1.num_truck == truck_2.truck_id_supply:
                    break
                else:
                    return truck_2.truck_id_supply

        return truck_1.num_truck


def truck_consumption(num_truck, num_truck_supply):
    for num_truck_b in num_truck:
        for num_truck_a in num_truck_supply:
            if num_truck_a.num_truck_departure != num_truck_b.num_truck:
                truck_con = num_truck_b.num_truck
                return truck_con


