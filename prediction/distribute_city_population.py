# Distributes the city population in four explicit disjoint states,
# Population p = x(t) + sum( u(tau,t),1, tau1) + sum(yi(tau,t),0,tau2) + z(t)

import os
import csv
import time
from pymongo import MongoClient
from prediction import airport
from prediction.distribution_initiation import init_distributions

city_matrix = airport.city_matrix
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
            for tau in range(length_of_infection_period + 1):
                if tau <= length_of_incubation_period:
                    city.lat_res[tau, t] = get_latent_f(tau) * city.get_latent_local(t - tau)
                city.inf_res[tau, t] = get_infectious_g(tau) * city.get_latent_local(t - tau)
        else:
            for tau in range(length_of_infection_period + 1):
                if tau <= length_of_incubation_period:
                    city.lat_res[tau, t] = 0
                city.inf_res[tau, t] = 0


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

    # Calculates all state equations for the city on the day in question. (7, 9 - 13).
    # The forecast is made over the time t0, t0 + 1, t0 + 2,..., t0 + T(forecast horizon)
    def calculate_state_equations_for_day(self, t):
        self.susceptible = int(self.apply_transport_operator(t, City.get_susceptible))
        inf = 0
        lat = 0
        for tau in range(0, length_of_infection_period + 1):
            if tau <= length_of_incubation_period:
                lat += self.get_latent(tau, t)
            inf += self.get_infectious(tau, t)
        self.latent = int(lat)
        self.infectious = int(inf)
        self.recovered = int(self.population - (self.susceptible + lat + inf))
        visualizable_object = {'City': self.name, 'Susceptible': self.susceptible, 'Latent': lat, 'Infectious': inf,
                               'Population': self.population}
        return visualizable_object

    # Transport operator omega for the travel matrix (8)
    def apply_transport_operator(self, t, input_function, **kwargs):
        help_sum = 0
        for j in range(len(city_matrix)):
            if not kwargs:
                func = input_function(city_list[j], t)
                mat = city_matrix[j][self.index_id] / city_list[j].population
                first_part = func * mat

                func = input_function(self, t)
                mat = city_matrix[self.index_id][j] / self.population
                second_part = func * mat
            else:
                func = input_function(city_list[j], kwargs.get('tau'), t)
                mat = city_matrix[j][self.index_id] / city_list[j].population
                first_part = func * mat

                func = input_function(self, kwargs.get('tau'), t)
                mat = city_matrix[self.index_id][j] / self.population
                second_part = func * mat
            help_sum += first_part - second_part
        if not kwargs:
            return input_function(self, t) + help_sum
        else:
            return input_function(self, kwargs.get('tau'), t) + help_sum

    # Returns the number of susceptible individuals for day t (9).
    def get_susceptible(self, t, **kwargs):
        if t not in self.sus_res:
            if t == 0:
                self.sus_res[t] = self.population * fraction_of_susceptible_population
            else:
                value = 0
                if (0, t - 1) not in self.lat_res:
                    if kwargs.get('local'):
                        value = self.get_latent_local(t - 1)
                        # self.lat_res[0, t - 1] = self.get_latent_local(t - 1)
                    else:
                        value = self.get_latent(0, t - 1)
                        # self.lat_res[0, t - 1] = self.get_latent(0, t - 1)
                if t - 1 not in self.sus_res:
                    self.sus_res[t - 1] = self.get_susceptible(t - 1)
                self.sus_res[t] = self.sus_res[t - 1] - value
        return self.sus_res[t]


    # (10) Returns the number of latent individuals on day t that were infected on day t-tau.
    def get_latent(self, tau, t):
        if t < 0:
            return 0
        if (tau, t) not in self.lat_res:
            if tau == 0:
                average_infected = (daily_infectious_contact_rate * self.get_susceptible(t)) / self.population
                number_of_infectious = 0
                for i in range(1, length_of_infection_period + 1):
                    number_of_infectious += self.get_latent(0, t - i) * get_infectious_g(i)
                return average_infected * number_of_infectious
            else:
                part_one = 1 - latent_becomes_infectious(tau - 1)
                part_two = self.apply_transport_operator(t - 1, City.get_latent, tau=(tau - 1))
                return part_one * part_two
        return self.lat_res[tau, t]

    def get_latent_boundary(self, t):
        return 0.00001 * self.population * 1.24 ** t

    # Returns the number of infectious individuals who were infected on day t - tau (11)
    def get_infectious(self, tau, t):
        if tau <= 0:
            self.inf_res[tau, t] = 0
        elif tau <= length_of_incubation_period:
            part_one = latent_becomes_infectious(tau - 1) * self.apply_transport_operator(t - 1, City.get_latent,
                                                                                          tau=(tau - 1))
            if (tau - 1, t - 1) not in self.inf_res:
                part_two = (1 - infectious_recovers(tau - 1)) * self.get_infectious(tau - 1, t - 1)
            else:
                part_two = (1 - infectious_recovers(tau - 1)) * self.inf_res[tau - 1, t - 1]
            self.inf_res[tau, t] = part_one + part_two
        elif tau <= length_of_infection_period - 1:
            if (tau - 1, t - 1) not in self.inf_res:
                self.inf_res[tau, t] = (1 - infectious_recovers(tau)) * self.get_infectious(tau - 1, t - 1)
            else:
                self.inf_res[tau, t] = (1 - infectious_recovers(tau)) * self.inf_res[tau - 1, t - 1]
        if (tau, t) in self.inf_res:
            return self.inf_res[tau, t]
        else:
            return 0

    # Number of individuals who became ill on day t. (12)
    def calculate_daily_morbidity(self, t):
        result = 0
        for tau in range(0, length_of_incubation_period + 1):
            result += latent_becomes_infectious(tau) * self.apply_transport_operator(t - 1, City.get_latent, tau=tau)
        return result

    # Modeled number of new ill individuals reported to the health registry. (13)
    def modeled_number_of_new_ill_individuals(self, t):
        return fraction_of_newly_ill_reported * self.calculate_daily_morbidity(t)

    # Calculates the number of latent individuals on day date who were infected on day date - tau. (15)
    def get_latent_local(self, t):
        if (0, t) not in self.lat_res:
            if t <= 0:
                return self.get_latent_boundary(t)
            else:
                if t not in self.sus_res:
                    factor = (daily_infectious_contact_rate * self.get_susceptible(t, local=True)) / self.population
                else:
                    factor = (daily_infectious_contact_rate * self.sus_res[t]) / self.population
                help_sum = 0
                for i in range(1, length_of_infection_period + 1):
                    if (0, t - i) in self.lat_res:
                        help_sum += self.lat_res[0, t - i] * get_infectious_g(i)
                    else:
                        help_sum += self.get_latent_local(t - i) * get_infectious_g(i)
                return factor * help_sum
        return self.lat_res[0, t]

    # Calculates the modeled number of of new ill individuals reported to the health registry on day date (16)
    def get_computed_new_sick_individuals_local(self, t):
        help_sum = 0
        for i in range(0, length_of_incubation_period + 1):
            help_sum += (get_latent_f(i) - get_latent_f(i + 1)) * self.get_latent_local(t - i)
        return help_sum * fraction_of_newly_ill_reported

    # Local influenza (19)
    def local_influenza(self):
        for tau in range(0, length_of_infection_period + 1):
            self.lat_res[0, -tau] = 0.00001 * self.population * 1.24 ** (-tau)
        self.sus_res[0] = fraction_of_susceptible_population * self.population

    pass

    # Compares a_i0(t) with b_i0(t) to find the initial date of the epidemic in city i_0.
    def align_local_and_global_times(self, observed_ill_individuals):
        t_max = observed_ill_individuals.index(max(observed_ill_individuals))
        print(t_max)
        t = 0
        last_max = -1
        current_max = self.get_computed_new_sick_individuals_local(t)
        while last_max < current_max:
            t += 1
            last_max = current_max
            current_max = self.get_computed_new_sick_individuals_local(t)
        t_hat_max = t - 1
        return t_max - t_hat_max

    # Initializes the pandemic process. This is defined as the first day at which at least one latent individual travels
    # from city i_0 to another directly connected city. (23)
    # The paper uses 1.24 as an estimate for the value mu, which is why we also chose to use this value as an estimate.

    def calculate_first_travel_day(self):
        temp_list = []
        max_sigma = max(city_matrix[self.index_id])
        for t in range(440):
            help_sum = 0
            for tau in range(0, length_of_incubation_period + 1):
                test = get_latent_f(tau)
                help_sum += test * 1.24 ** (-tau)
            temp_list.append((self.get_latent_local(t) / self.population) * help_sum * max_sigma)
        temp_list = [element for element in temp_list if element >= 1]
        if len(temp_list) >= 1:
            return temp_list.index(min(temp_list))
        else:
            return -1

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
    hong_kong = city_list[9]
    hong_kong.local_influenza()
    # first_travel_day = hong_kong.calculate_first_travel_day()
    first_travel_day = 0
    initiate_initial_conditions(first_travel_day)

    return hong_kong


initiate_validation_results()
hong_kong = city_list[9]
new_york = city_list[34]

for t in range(0, 440):
    hong_kong.calculate_state_equations_for_day(t)
    print(str(t) + ": " + str(hong_kong))
# # init_city_list()
# init_dummy_city_list()
# # noinspection PyRedeclaration
# city_matrix = airport.create_dummy_matrix()
# City.index_city_id = 9
# hong_kong = city_list[9]
# hong_kong.local_influenza()
#
# first_travel_day = hong_kong.calculate_first_travel_day()
# initiate_initial_conditions(0)
# # forecast(9, 10)
