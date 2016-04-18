# Distributes the city population in four explicit disjoint states,
# Population p = x(t) + sum( u(tau,t),1, tau1) + sum(yi(tau,t),0,tau2) + z(t)

import csv
import os

from pymongo import MongoClient
from pandas import *

from airport import airport
from prediction.distribution_initiation import init_distributions

city_matrix = airport.create_dummy_matrix()
infection_distribution = init_distributions()
city_list = []
city_population_file = os.path.abspath(os.path.dirname(__file__)) + '/data/citypopulation.csv'
dummy_population_file = os.path.abspath(os.path.dirname(__file__)) + '/data/dummypopulation.csv'

length_of_incubation_period = 2  # tau1
length_of_infection_period = 8  # tau2
daily_infectious_contact_rate = 1.055  # lambda #TODO Find a correct lambda value
fraction_of_susceptible_population = 0.641  # alpha #TODO Find a correct alpha value
fraction_of_newly_ill_reported = 0.3  # beta. #TODO Set a correct beta value
forecast_horizon = 440  # T

mongo_uri = os.environ.get('MONGOLAB_URI')

if mongo_uri:
    client = MongoClient(mongo_uri)
    print('Connected to MongoDB')
    db = client.heroku_k99m6wnb
    cities = db.cities
else:
    cities = 0
    print('Couldnt connect to DB')


def init_city_list():
    if cities is not 0:
        if len(city_list) == 0:
            index = 0
            for doc in cities.find():
                city_list.append(City(index, doc['city'], doc['population'], doc['location']))
                index += 1
    else:
        with open(city_population_file) as csvfile:
            reader = csv.reader(csvfile)
            index = 0
            for row in reader:
                city_list.append(City(index, row[0], float(row[1]), {}))
                index += 1


def init_dummy_city_list():
    with open(dummy_population_file) as csvfile:
        reader = csv.reader(csvfile)
        index = 0
        for row in reader:
            city_list.append(City(index, row[0], float(row[1]), {}))
            index += 1


# return f(time) (2)
def get_latent_f(t):
    return float(infection_distribution[0][t])


# return g(time) (3)
def get_infectious_g(t):
    return float(infection_distribution[1][t])


# return h(time) (4)
def get_removed_h(t):
    return float(infection_distribution[2][t])


# Returns the probability that a latent individual becomes infectious on day t (5) gamma(t)
def latent_becomes_infectious(t):
    return float(infection_distribution[3][t])


# Returns the probability that an infectious individual recovers on day t   (6) delta(t)
def infectious_recovers(t):
    return float(infection_distribution[4][t])


# Computes the initial conditions for all cities (24, 25, 26)
def initiate_initial_conditions(t):
    for city in city_list:
        city.sus_res[t] = city.population * fraction_of_susceptible_population
        if city.index_id == City.index_city_id:
            for tau in range(1, length_of_infection_period + 1):
                if tau <= length_of_incubation_period:
                    city.lat_res[tau, t] = get_latent_f(tau) * city.lat_res[0, t - tau + 1]
                city.inf_res[tau, t] = get_infectious_g(tau) * city.lat_res[0, t - tau + 1]
        else:
            for tau in range(length_of_infection_period + 1):
                if tau <= length_of_incubation_period:
                    city.lat_res[tau, t] = 0
                city.inf_res[tau, t] = 0


def initiate_influenza():
    for city in city_list:
        city.sus_res[0] = city.population * fraction_of_susceptible_population  # Equation 20
        if city.index_id == City.index_city_id:
            city.lat_res[0, 0] = 0.00001 * city.population      # Equation 19
            city.inf_res[0, 0] = 0
            for tau in range(1, length_of_infection_period + 1):
                city.lat_res[0, -tau] = city.lat_res[0, 1 - tau] * (1 / 1.24)
                city.inf_res[0, -tau] = 0
        else:
            for tau in range(length_of_infection_period + 1):
                city.lat_res[0, -tau] = 0
                city.inf_res[0, -tau] = 0


def calculate_state_equations(t):
    for city in city_list:
        tmp_sum = 0
        for tau in range(1, length_of_infection_period + 1):
            tmp_sum += city.apply_omega_latent(City.get_latent_iterative, 0, t - tau) * get_infectious_g(tau)
            tmp_sum += city.inf_res[tau, t]
        city.lat_res[0, t] = daily_infectious_contact_rate * (city.sus_res[t] / city.population) * tmp_sum
        city.inf_res[0, t] = 0

        city.sus_res[t + 1] = city.get_sus_iterative(t) - city.lat_res[0, t]

        for tau in range(1, length_of_infection_period + 1):
            if tau <= length_of_incubation_period:
                city.lat_res[tau, t + 1] = (1 - latent_becomes_infectious(tau)) * city.apply_omega_latent(City.get_latent_iterative, tau, t)
                city.inf_res[tau, t + 1] = latent_becomes_infectious(tau) * city.apply_omega_latent(City.get_latent_iterative, tau, t) + (1 - infectious_recovers(tau)) * city.inf_res[tau, t]
            else:
                city.inf_res[tau, t + 1] = (1 - infectious_recovers(tau)) * city.inf_res[tau, t]
        city.susceptible = int(city.get_sus_iterative(t))


class City:
    index_city_id = 0

    def __init__(self, index_id, name, population, location):
        self.index_id = index_id
        self.name = name
        self.population = float(population)
        self.susceptible = 0
        self.latent = 0
        self.infectious = 0
        self.recovered = 0
        self.initial_date_of_epidemic = 0
        self.sus_res = {}
        self.lat_res = {}
        self.inf_res = {}
        self.location = location


    def get_latent_iterative(self, tau, t):
        return self.lat_res[tau, t]


    def get_sus_iterative(self, t):
        return self.sus_res[t]


    def apply_omega_latent(self, func, tau, t):
        help_sum = 0
        for j in range(len(city_matrix)):
            aj = func(city_list[j], tau, t) * city_matrix[j][self.index_id] / city_list[j].population
            ai = func(self, tau, t) * city_matrix[self.index_id][j] / self.population
            help_sum += aj - ai
        result = func(self, tau, t) + help_sum
        tmp = 0
        for tau in range(length_of_incubation_period + 1):
            tmp += get_latent_f(tau)
        if result * tmp < 1:
            result = 0
        return result


    def apply_omega_sus(self, func, t):
        help_sum = 0
        for j in range(len(city_matrix)):
            aj = func(city_list[j], t)
            sigma_ji = city_matrix[j][self.index_id] / city_list[j].population

            ai = func(self, t)
            sigma_ij = city_matrix[self.index_id][j] / self.population
            help_sum += (aj * sigma_ji) - (ai * sigma_ij)
        result = func(self, t) + help_sum
        return result

    # Equation (12) and (13)
    def get_daily_computed_morbidity(self, t):
        result = 0
        for tau in range(0, length_of_incubation_period + 1):
            result += latent_becomes_infectious(tau) * self.lat_res[tau, t - 1]
        return fraction_of_newly_ill_reported * result


    # Adds the four states in the city class to ensure that they are equal to the population count.
    def calculate_city_population(self):
        return int(self.susceptible + self.latent + self.infectious + self.recovered)

    def __str__(self):
        return "ID: " + str(self.index_id) + " \tName: " + self.name + " \t Population: \t" + str(self.population) + \
               " \t x: " + str(self.susceptible) + " \t u: " + str(self.latent) + "     \t y: " + str(self.infectious) + \
               " \t z: " + str(self.recovered)


def initiate_validation_results():
    init_dummy_city_list()
    city_matrix = airport.create_dummy_matrix()
    City.index_city_id = 9
    first_travel_day = 0
    initiate_influenza()
    initiate_initial_conditions(first_travel_day)


initiate_validation_results()
hong_kong = city_list[9]
new_york = city_list[0]
days = 300
result_matrix = []
tmp_res = []

for city in city_list:
    tmp_res.append(city.name)
result_matrix.append(tmp_res)

tmp_res = []
for t in range(0, days):
    calculate_state_equations(t)
    # print(hong_kong)

    for city in city_list:
        tmp_res.append(int(city.get_daily_computed_morbidity(t + 1)))
        # tmp_res.append(int(city.lat_res[0, t]))
    result_matrix.append(tmp_res)
    tmp_res = []


s = [[str(e) for e in row] for row in result_matrix]
lens = [max(map(len, col)) for col in zip(*s)]
fmt = '\t'.join('{{:{}}}'.format(x) for x in lens)
table = [fmt.format(*row) for row in s]
print('\n'.join(table))
# print(DataFrame(result_matrix))
