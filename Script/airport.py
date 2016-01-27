import csv
import requests
from pprint import pprint



class OriginTravel:
    originCount = 0

    def __init__(self, origin, destination, passengers):
        self.origin = origin
        self.destination = destination
        self.passengers = passengers
        OriginTravel.originCount += 1

    def __str__(self):
        return 'Origin: ' + self.origin + ' Destination ' + self.destination + ' Passengers: ' + str(self.passengers)


class City:

    def __init__(self, name, population, airport_code):
        self.name = name
        self.population = population
        self.airport_code = airport_code


class Airport:
    def __init__(self, airportcode):
        self.airportcode = airportcode


def sort_per_origin(list_input):
    sorted_dict = sorted(list_input, key=lambda k: k['ORIGIN'])
    current_origin = OriginTravel(None, None, 0)
    result = []
    for row in sorted_dict:
        if row['ORIGIN'] != current_origin.origin:
            result.append(current_origin)
            current_origin = OriginTravel(row['ORIGIN'], row['DEST'], int(float(row['PASSENGERS'])))
        else:
            current_origin.passengers += int(float(row['PASSENGERS']))
    result.pop(0)
    return result


def sort_per_destination(list_input):
    sorted_dict = sorted(list_input, key=lambda k: k['DEST'])
    current_destination = OriginTravel(None, None, 0)
    result = []
    for row in sorted_dict:
        if row['DEST'] != current_destination.destination:
            result.append(current_destination)
            current_destination = OriginTravel(row['ORIGIN'], row['DEST'], int(float(row['PASSENGERS'])))
        else:
            current_destination.passengers += int(float(row['PASSENGERS']))
    result.pop(0)
    return result


#def get_airport_info(airport_code):

def __main__():
    with open('t100market.csv') as csvfile:
        reader = csv.DictReader(csvfile)
        destination_list = sort_per_destination(reader)

    with open('t100market.csv') as csvfile:
        reader = csv.DictReader(csvfile)
        origin_list = sort_per_origin(reader)

    sorted_destinations = sorted(destination_list, key=lambda k: k.passengers)
    sorted_origins = sorted(origin_list, key=lambda k: k.passengers)

    for travel in sorted_destinations[len(sorted_destinations)-50:]:
        print(travel.__str__())

    for travel in sorted_origins[len(sorted_origins)-50:]:
        print(travel.__str__())

    params = {'user_key': 'eb6c3e8d6fb060a9a99f7b9fd061013c'}
    r = requests.get('https://airport.api.aero/airport', params=params)

    pprint(r.content)


__main__()
