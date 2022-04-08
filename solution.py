"""
Examples of how to run:

solution.py file origin destination
python -m solution example2.csv YOT LOM
python -m solution example2.csv YOT LOM --bags=1 --returns=2
"""
import argparse
import sys
import csv
import json
import datetime
from datetime import timedelta


def inputs():
    """
    Handles input arguments from command line.

    :return: Parsed inputs
    """
    def value_check(value):
        if int(value) < 0:
            raise argparse.ArgumentTypeError(f"{value} is an invalid input, input value between 0 and 100")
        return int(value)

    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="data file")
    parser.add_argument("origin", help="origin airport code")
    parser.add_argument("destination", help="destination airport code")
    parser.add_argument("--bags", help="number of bags", type=value_check)
    parser.add_argument("--returns", help="return flights after number of days", type=value_check)
    return parser.parse_args()


def time_diff(first: dict, second: dict) -> bool:
    """
    Checks if layover time between flights is within parameters.

    :param first: Coming flight
    :param second: Leaving flight
    :return: True/False
    """
    first = datetime.datetime.strptime(first['arrival'], '%Y-%m-%dT%H:%M:%S')
    second = datetime.datetime.strptime(second['departure'], '%Y-%m-%dT%H:%M:%S')
    if timedelta(hours=1) <= second - first <= timedelta(hours=6):
        return True
    return False


def departures(flight: list[dict], data_list: list[dict]) -> list[dict]:
    """
    Finds all departure flights from particular airport.

    :param flight: Flight for which subsequent flights are found
    :param data_list: Dataset of flights info stored in list
    :return: List of dictionaries
    """
    flight_list = []
    for x in data_list:
        if x['origin'] == flight[len(flight) - 1]['destination']:
            if time_diff(flight[len(flight) - 1], x):
                check = True
                for y in flight:                            # no repeating airports
                    if x['destination'] == y['origin']:
                        check = False
                        break
                if check:
                    flight_list.append(x)
    return flight_list


def travel_time(trip: list[dict], start: str, end: str) -> datetime or bool:
    """
    Calculates total travel time of a trip.

    :param trip: List with connected flights creating a trip
    :param start: Origin airport code of a trip
    :param end: Destination airport code of a trip
    :return: Datetime value of total travel time for a trip
    """
    start_travel = None
    end_travel = None
    for i in trip:
        if i['origin'] == start:
            start_travel = datetime.datetime.strptime(i['departure'], '%Y-%m-%dT%H:%M:%S')
        if i['destination'] == end:
            end_travel = datetime.datetime.strptime(i['arrival'], '%Y-%m-%dT%H:%M:%S')
    if start_travel and end_travel:
        return end_travel - start_travel
    return False


def read_file(fp: str) -> list[dict]:
    """
    Reads file by lines, stores in list.

    :param fp: String containing dataset with flight info
    :return: List of dictionaries with flight info
    """
    data_list = []
    with open(fp, newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            data_list.append(row)
    return data_list


def remove_flights(bags_count: int, data_list: list[dict]) -> list[dict]:
    """
    Remove flights with insufficient number of allowed bags.

    :param bags_count: Searched number of bags
    :param data_list: List of dictionaries with flight info
    :return: Updated list of dictionaries with flight into
    """
    if bags_count:
        for i in data_list.copy():
            if int(i['bags_allowed']) < bags_count:
                data_list.remove(i)
    return data_list


def searching(data_list: list[dict], start: str, end: str) -> list:
    """
    First loop finds all flights from origin airport.
    Second loop finds subsequent flights and joins them with previous.

    :param data_list: List of dictionaries with flight info
    :param start: Origin airport code of a trip
    :param end: Destination airport code of a trip
    :return: List with connected flights creating trips.
    """
    results = []
    trips = []
    for i in data_list:
        if i['origin'] == start:
            if i['destination'] == end:
                results.append([i])
            else:
                trips.append([i])

    i = 0
    while trips:
        departure_list = departures(trips[i], data_list)
        if not departure_list:
            trips.pop(i)
        else:
            for j in departure_list:
                if j['destination'] == end:
                    results.append([*trips[i], j])
                else:
                    trips.append([*trips[i], j])
            trips.pop(i)
    return results


def returns(results: list, results_return: list, destination_days: int):
    """
    Finds first return flight after specified number of days at destination.

    :param results: List with connected flights creating trips.
    :param results_return: List with connected flights for return trips.
    :param destination_days: Number of days spent at destination before returning.
    :return: List with connected flights including return creating trips.
    """
    result = []
    for num, i in enumerate(results):
        first = datetime.datetime.strptime(i[len(i)-1]['arrival'], '%Y-%m-%dT%H:%M:%S')
        for j in results_return:
            second = datetime.datetime.strptime(j[0]['departure'], '%Y-%m-%dT%H:%M:%S')
            if first + timedelta(days=destination_days) < second:
                temp = results[num].copy()
                temp.append(j[0])
                result.append(temp)
                break
    return result


def output_list(results: list, start: str, end: str, bags_count: int) -> list:
    """
    Creates dictionaries with output format, stores them in list.

    :param results: List with connected flights creating trips
    :param start: Origin airport code
    :param end: Destination airport code
    :param bags_count: Searched number of bags
    :return: List with output information.
    """
    final = []
    for i in results:
        total_price = 0
        bags_allowed = sys.maxsize
        for j in i:
            if bags_allowed > int(j['bags_allowed']):
                bags_allowed = int(j['bags_allowed'])
            total_price += float(j['base_price']) + float(j['bag_price']) * bags_count
        travel_duration = str(travel_time(i, start, end))
        if travel_time(i, end, start):
            travel_duration = str(travel_time(i, start, end) + travel_time(i, end, start))
        info = {'flights': i, 'origin': start, 'destination': end, 'bags_allowed': bags_allowed,
                'bags_count': bags_count, 'total_price': total_price, 'travel_time': travel_duration}
        final.append(info)

    def sorting(e):                     # sort trips by total price
        return e['total_price']

    final.sort(key=sorting)
    return final


def main():
    args = inputs()
    fp = args.file
    start = args.origin
    end = args.destination
    bags_count = 0
    if args.bags:                                   # optional argument --bags=
        bags_count = args.bags
    data_list = read_file(fp)
    data_list = remove_flights(bags_count, data_list)
    results = searching(data_list, start, end)
    if args.returns or args.returns == 0:           # optional argument --returns=
        destination_days = args.returns
        results_return = searching(data_list, end, start)
        results = returns(results, results_return, destination_days)
    final = output_list(results, start, end, bags_count)
    if not final:
        return print('No flights found')
    return print(json.dumps(final, indent=4))


if __name__ == "__main__":
    main()
