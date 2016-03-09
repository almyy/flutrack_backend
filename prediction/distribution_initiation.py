import csv

from prediction import distribute_city_population as temp

city_population_file = 'C:/Users/mikaelrs/Skole/Master/Repositories/flutrack_backend/' \
                       'prediction/data/citypopulation.csv'
infection_distribution_file = 'C:/Users/mikaelrs/Skole/Master/Repositories/flutrack_backend/' \
                              'prediction/data/infection_distribution.csv'


def init_distributions():
    infection_distribution = []
    with open(infection_distribution_file) as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            infection_distribution.append(row)
    return infection_distribution


def init_city_list():
    city_list = []
    with open(city_population_file) as csvfile:
        reader = csv.reader(csvfile)
        index = 0
        for row in reader:
            city_list.append(temp.City(index, row[0], float(row[1])))
            index += 1
    return city_list
