import json

# Ф-ї для зчитування даних: -----------------------------------------------------------------
def read_data(file):
    with open(file, "r", encoding="UTF-8") as read_file:
        data = json.load(read_file)
    return data


def all_stops_from_json(struct):
    return [stop["name"] for stop in struct]

def all_trams_names(data):
    return [tram["short_name"] for tram in data]

# Ф-ї для внутрішньої роботи запитів: --------------------------------------------------------------

def all_direct_stops_names(tram):
    return [stop["name"] for stop in tram["direct_stops"]]


def all_reverse_stops_names(tram):
    return [stop["name"] for stop in tram["reverse_stops"]]


def tram_has_stop(tram, stop_name): # чи має трамвай задану зупинку
    if list(filter(lambda 
                stop: stop['name'] == stop_name, 
                tram["direct_stops"])):
        return True
    return False


def trams_for_stop(stop_name, data): # які трамваї мають задану зупинку
    trams = []
    for tram in data:
        if tram_has_stop(tram, stop_name):
            trams.append(tram)
    return trams

# індекси зупинок у списках зупинок певного трамвая:
def direct_indexes(tram, stop_name1, stop_name2): 
    stop1 = [stop for stop in tram["direct_stops"] if stop["name"]==stop_name1][0]
    stop2 = [stop for stop in tram["direct_stops"] if stop["name"]==stop_name2][0]
    return tram["direct_stops"].index(stop1), tram["direct_stops"].index(stop2)


def reverse_indexes(tram, stop_name1, stop_name2): 
    stop1 = [stop for stop in tram["reverse_stops"] if stop["name"]==stop_name1][0]
    stop2 = [stop for stop in tram["reverse_stops"] if stop["name"]==stop_name2][0]
    return tram["reverse_stops"].index(stop1), tram["reverse_stops"].index(stop2)


def tram_change_stops(tram1, tram2): # зупинки для пересадки між заданими трамваями
    stops = []
    for st in tram1["direct_stops"]:
        if tram_has_stop(tram2, st["name"]):
            stops.append(st["name"])
    return stops


# шлях від зупинки до зупинки без пересадок - обидві мусять бути в маршруті трамвая
def no_tram_change_route(tram, stop_name1, stop_name2):
    route = {}
    route["tram"] = tram["short_name"]
    i1, i2 = direct_indexes(tram, stop_name1, stop_name2)
    if i1<i2:
        route["stops"] = [stop["name"] for stop in tram["direct_stops"][i1:i2+1]]
    else:
        ri1, ri2 = reverse_indexes(tram, stop_name1, stop_name2)
        route["stops"] = [stop["name"] for stop in tram["reverse_stops"][ri1:ri2+1]]
    return route


# список всіх можливих шляхів - з пересадками і без
def routes(stop_name1, stop_name2, data):
    result = []
    for tram in trams_for_stop(stop_name1, data):
        if tram_has_stop(tram, stop_name2):
            route = []
            route.append(no_tram_change_route(tram, stop_name1, stop_name2))
            result.append(route)
        else:
            for tram2 in trams_for_stop(stop_name2, data):
                if tram_has_stop(tram2, stop_name2):
                    for change_stop in tram_change_stops(tram, tram2):
                        route = []
                        route.append(no_tram_change_route(tram, stop_name1, change_stop))
                        route.append(no_tram_change_route(tram2, change_stop, stop_name2))
                        result.append(route)
    return result


# к-ть зупинок одним шляхом
def stops_count(route):
    count = 0
    for part in route:
        count += len(part["stops"])
    return count


# найкоротший шлях. список трамваїв та зупинок, які треба ними проїхати
def shortest_route(stop_name1, stop_name2, data):
    _routes = routes(stop_name1, stop_name2, data)
    min_stops_count = stops_count(_routes[0])
    index = 0
    for i in range(1,len(_routes)):
        count = stops_count(_routes[i])
        if count < min_stops_count:
            min_stops_count = count
            index = i
    return _routes[index]


# чи потрібна пересадка
def tram_change_needed(stop_name1, stop_name2, data):
    route = shortest_route(stop_name1, stop_name2, data)
    return len(route)>1

# Ф-ї взаємодії з користувачем: ---------------------------------------------------------------------------

# ввід назви зупинки, яка гарантовано є у списку
def stop_input(stops_names):
    stop_name = input()
    while stop_name not in stops_names:
        print ("Назва зупинки введена неправильно, такої зупинки немає у списку. Спробуйте ще раз:")
        stop_name = input()
    return stop_name


# повертає весь словник з даними про трамвай за введеною назвою
def tram_by_name(data):
    name = input()
    while name not in all_trams_names(data):
        print ("Введеного вами трамвая немає у списку. Спробуйте ще раз:")
        name = input()
    return [tram for tram in data if tram["short_name"]==name][0]


# вивід знайденого шляху
def route_output(route):
    for part in route:
        print(f'\nСядьте на трамвай {part["tram"]} та ' \
        f'проїдьте до зупинки {part["stops"][-1]}. Тут потрібно вийти.')


# вивід найкоротшого шляху за заданими двома зупинками
def shortest_route_request(data, stops_names):
    print("Введіть початкову зупинку: ")
    stop_name1 = stop_input(stops_names)
    print("Введіть кінцеву зупиинку:")
    stop_name2 = stop_input(stops_names)
    route = shortest_route(stop_name1, stop_name2, data)
    route_output(route)


# вивід номерів трамваїв, що їдуть на задану зупинку
def trams_for_stop_request(data, stops_names):
    print("Введіть назву зупинки:")

    stop_name = stop_input(stops_names)

    trams = trams_for_stop(stop_name, data)

    if not trams:
        print(f"На зупинку '{stop_name}' не їздять трамваї.")
    else:
        print(f"Трамваї, що їдуть на зупинку '{stop_name}':")
        for tram in trams:
            print(tram["short_name"])




# вивід так чи ні якщо заданий номер трамвая має задану зупинку
def tram_has_stop_request(data, stops_names):
    print("Введіть номер трамвая:")

    tram_data = tram_by_name(data)

    print("Введіть назву зупинки:")

    stop_name = stop_input(stops_names)

    if tram_has_stop(tram_data, stop_name):
        print(f"Так, трамвай {tram_data['short_name']} має зупинку '{stop_name}'.")
    else:
        print(f"Ні, трамвай {tram_data['short_name']} не має зупинки '{stop_name}'.")



# вивід можливих зупинок для пересадки між двома заданими трамваями
def tram_change_stops_request(data, stops_names):
    print("Введіть номер першого трамвая:")

    tram1_data = tram_by_name(data)

    print("Введіть номер другого трамвая:")

    tram2_data = tram_by_name(data)

    change_stops = tram_change_stops(tram1_data, tram2_data)

    if not change_stops:
        print(f"Немає можливих зупинок для пересадки між трамваями {tram1_data['short_name']} та {tram2_data['short_name']}.")
    else:
        print(f"Можливі зупинки для пересадки між трамваями {tram1_data['short_name']} та {tram2_data['short_name']}:")
        for stop in change_stops:
            print(stop)


# вивід всіх зупинок заданого трамвая
def all_tram_stops_request(data, stops_names):
    print("Введіть номер трамвая:")

    tram_data = tram_by_name(data)

    print(f"Зупинки для трамвая {tram_data['short_name']}:")

    for stop in all_direct_stops_names(tram_data):
        print(stop)

    for stop in all_reverse_stops_names(tram_data):
        print(stop)


# так чи ні, якщо потрібна пересадка між двома заданими зупинками
def tram_change_neeeded_request(data, stops_names):
    print("Введіть початкову зупинку: ")
    stop_name1 = stop_input(stops_names)
    print("Введіть кінцеву зупинку:")
    stop_name2 = stop_input(stops_names)

    change_needed = tram_change_needed(stop_name1, stop_name2, data)

    if change_needed:
        print(f"Так, потрібна пересадка між зупинками '{stop_name1}' та '{stop_name2}'.")
    else:
        print(f"Ні, пересадка не потрібна між зупинками '{stop_name1}' та '{stop_name2}'.")



# Меню:----------------------------------------------------------------------------
options={
    "1":shortest_route_request,
    "2":trams_for_stop_request,
    "3":tram_has_stop_request,
    "4":tram_change_stops_request,
    "5":all_tram_stops_request,
    "6":tram_change_neeeded_request,
    "0":0
    }

def choice_input():
    choice=input()
    is_valid = choice in options
    while is_valid==False:
        print("Ви ввели неправильний символ! \n Введіть один з символів, запропонованих вище:")
        choice=input()
        is_valid = choice in options
    return choice

def menu():
    print("\n Введіть 1, якщо ви хочете дізнатися найкоротший шлях за заданими двома зупинками.")
    print("Введіть 2, якщо ви хочете дізнатися номери трамваїв, що їдуть на задану зупинку.")
    print("Введіть 3, якщо ви хочете перевірити, чи має заданий трамвай задану зупинку.")
    print("Введіть 4, якщо ви хочете знати можливі зупинки для пересадки між трамваями.")
    print("Введіть 5, якщо ви хочете дізнатися всі зупинки для заданого трамвая.")
    print("Введіть 6, якщо ви хочете перевірити, чи потрібна пересадка між двома заданими зупинками.")
    print("Введіть 0, якщо ви хочете вийти з програми.")
    choice = choice_input()
    return choice


if __name__ == "__main__":
    s = read_data("data/tram_stops.json")
    d = read_data("data/trams_info.json")
    _stops = all_stops_from_json(s)
    choice = menu()
    while choice!='0':
        options[choice](d, _stops)
        choice = menu()
