import csv
import os

from pymongo import MongoClient

from airport import airport
from prediction.distribution_initiation import init_distributions

city_matrix = airport.create_dummy_matrix()
# city_matrix = airport.create_grais_matrix()
# city_matrix = airport.get_travel_matrix()
infection_distribution = init_distributions()
city_list = []
city_population_file = os.path.abspath(os.path.dirname(__file__)) + '/data/data.csv'
dummy_population_file = os.path.abspath(os.path.dirname(__file__)) + '/data/dummypopulation.csv'
grais_population_file = os.path.abspath(os.path.dirname(__file__)) + '/data/grais_population.csv'

length_of_incubation_period = 2  # tau1
length_of_infection_period = 8  # tau2
daily_infectious_contact_rate = 1.055  # lambda #TODO Find a correct lambda value
fraction_of_susceptible_population = 0.641  # alpha #TODO Find a correct alpha value
fraction_of_newly_ill_reported = 0.3  # beta. #TODO Set a correct beta value

forecast_horizon = 440  # T
forecast_beginning = 164    # 12. juni
periodic_swing_T1 = 275     # 1. October
periodic_swing_T2 = 92     # 1. April

monthly_scaling_south_north = {-1: [0.10, 0.25, 0.55, 0.70, 0.85, 1.0, 1.0, 0.85, 0.70, 0.55, 0.25, 0.10],
                               0: [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                               1: [1.0, 0.85, 0.70, 0.55, 0.25, 0.10, 0.10, 0.25, 0.55, 0.70, 0.85, 1.0]}


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
            for doc in cities.find():
                city_list.append(City(doc['index'], doc['city'], doc['population'], doc['location'], int(doc['zone'])))
    else:
        with open(city_population_file) as csvfile:
            reader = csv.reader(csvfile)
            index = 0
            for row in reader:
                city_list.append(City(index, row[0], float(row[1]), {}, 0))
                index += 1


def init_dummy_city_list():
    with open(dummy_population_file) as csvfile:
        reader = csv.reader(csvfile)
        index = 0
        for row in reader:
            city_list.append(City(index, row[0], float(row[1]), {}, int(row[2])))
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
    result = (get_latent_f(t) - get_latent_f(t + 1)) / get_latent_f(t)
    return result


# Returns the probability that an infectious individual recovers on day t   (6) delta(t)
def infectious_recovers(t):
    result = (get_removed_h(t + 1) - get_removed_h(t)) / get_infectious_g(t)
    return result


# Returns the correct period for flu. (Between October and April - True/False).
def calculate_seasonality_rl(t):
    current_date = (forecast_beginning + t) % 365
    season = 1 if periodic_swing_T2 < current_date < periodic_swing_T1 else -1
    return season


# Returns the correct month for seasonality of flu.
def calculate_seasonality_g(t):
    current_date = (forecast_beginning + t) % 365
    month = current_date // 31
    return month


# Computes the initial conditions for all cities (24, 25, 26)
def initiate_initial_conditions(t):
    for city in city_list:
        city.sus_res[t] = city.population * fraction_of_susceptible_population
        if city.id == City.index_city_id:
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
        if city.id == City.index_city_id:
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
    month = calculate_seasonality_g(t)
    # month = calculate_seasonality_rl(t)
    for city in city_list:
        seasonality = monthly_scaling_south_north[city.zone][month]
        # seasonality = 0.1 if city.zone == month else 1
        tmp_sum_lat = 0
        for tau in range(1, length_of_infection_period + 1):
            tmp_sum_lat += city.apply_omega_latent(0, t - tau) * get_infectious_g(tau)
        city.lat_res[0, t] = seasonality * daily_infectious_contact_rate * (city.sus_res[t] / city.population) * tmp_sum_lat
        city.inf_res[0, t] = 0

        city.sus_res[t + 1] = city.apply_omega_susceptible(t) - city.lat_res[0, t]

        for tau in range(1, length_of_incubation_period + 1):
                res = city.apply_omega_latent(tau, t)
                city.lat_res[tau, t + 1] = (1 - latent_becomes_infectious(tau)) * res
                city.inf_res[tau, t + 1] = latent_becomes_infectious(tau) * res + ((1 - infectious_recovers(tau)) * city.inf_res[tau, t])

        for tau in range(length_of_incubation_period + 1, length_of_infection_period + 1):
            city.inf_res[tau, t + 1] = ((1 - infectious_recovers(tau)) * city.inf_res[tau, t])

        morbidity = 0
        for tau in range(0, length_of_incubation_period + 1):
            morbidity += latent_becomes_infectious(tau) * city.lat_res[tau, t]
        city.daily_morbidity.append(fraction_of_newly_ill_reported * morbidity)


class City:
    index_city_id = 0

    def __init__(self, id, name, population, location, zone):
        self.id = id
        self.name = name
        self.population = float(population)
        self.sus_res = {}
        self.lat_res = {}
        self.inf_res = {}
        self.daily_morbidity = []
        self.location = location
        self.zone = zone
        self.peak_day = 0

    def apply_omega_susceptible(self, t):
        help_sum = 0
        for j in range(len(city_matrix)):
            aj = city_list[j].sus_res[t] * city_matrix[j][self.id] / city_list[j].population
            ai = self.sus_res[t] * city_matrix[self.id][j] / self.population
            help_sum += aj - ai
        result = self.sus_res[t] + help_sum
        return result

    def apply_omega_latent(self, tau, t):
        help_sum = 0
        for j in range(len(city_matrix)):
            aj = city_list[j].lat_res[tau, t] * city_matrix[self.id][j] / city_list[j].population
            ai = self.lat_res[tau, t] * city_matrix[j][self.id] / self.population
            help_sum += aj - ai
        result = self.lat_res[tau, t] + help_sum
        tmp = 0
        for tau in range(length_of_incubation_period + 1):
            tmp += get_latent_f(tau)
        if result * tmp < 1:
            result = 0
        return result


    def __str__(self):
        return "ID: " + str(self.id) + " \tName: " + self.name + " \t Population: \t" + str(self.population)


def initiate_validation_results(index_city):
    # init_dummy_city_list()
    init_city_list()
    City.index_city_id = index_city
    first_travel_day = 0
    initiate_influenza()
    initiate_initial_conditions(first_travel_day)
    return city_list[City.index_city_id]


def forecast():
    index_city = 14
    initiate_validation_results(index_city)
    forecast_obj = []
    for t in range(0, forecast_horizon):
        calculate_state_equations(t)
        data = []
        for city in city_list:
            data.append({'city': city.name, 'morbidity': city.daily_morbidity[t], 'location': city.location})
        forecast_obj.append(data)
    return forecast_obj
