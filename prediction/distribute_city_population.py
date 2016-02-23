# Distributes the city population in four explicit disjoint states,
# Population p = x(t) + sum( u(tau,t),1, tau1) + sum(yi(tau,t),0,tau2) + z(t)
import csv
from prediction import airport

length_of_incubation_period = 2  # tau1
length_of_infection_period = 8  # tau2
daily_infectious_contact_rate = 1  # lambda #TODO Find a correct lambda value
fraction_of_susceptible_population = 0.641  # alpha #TODO Find a correct alpha value
fraction_of_newly_ill_reported = 0.99  # beta. #TODO Set a correct beta value
infection_distribution = []
city_list = []
city_population_file = 'C:/Users/mikaelrs/Skole/Master/Repositories/flutrack_backend/' \
                       'prediction/data/citypopulation.csv'
infection_distribution_file = 'C:/Users/mikaelrs/Skole/Master/Repositories/flutrack_backend/' \
                              'prediction/data/infection_distribution.csv'
first_travel_day_of_latent_individual = 1
forecast_horizon = 440


# return f(time)
def get_latent_f(time):
    return float(infection_distribution[0][time])


# return g(time)
def get_infectious_g(time):
    return float(infection_distribution[1][time])


# return h(time)
def get_removed_h(time):
    return float(infection_distribution[2][time])


class City:
    index_city_id = 0

    def __init__(self, index_id, name, population):
        self.index_id = index_id
        self.name = name
        self.population = population
        self.susceptible = int(round(self.population * fraction_of_susceptible_population, 0))
        self.latent = 0
        self.infectious = 0
        self.recovered = int(self.population - self.susceptible)
        self.initial_date_of_epidemic = 0
        self.sus_res = {}
        self.lat_res = {}

    # Initiate the initial conditions for a index cit x_i0
    def initiate_initial_conditions(self):
        # TODO Implement initial conditions
        self.calculate_initial_date_of_epidemic()

        pass

    # Calculates all state equations for the city on the day in question.
    def calculate_state_equations_for_day(self, tau, t):
        matrix = airport.city_matrix
        self.susceptible = self.apply_transport_operator(matrix, t, City.get_susceptible_mem_local) - \
                           self.get_latent_mem_local(0, t)
        self.latent = int(round((1 - float(infection_distribution[3][tau])) * \
                                self.apply_transport_operator(matrix, t, City.get_latent_mem_local, tau=tau), 0))

    def apply_transport_operator(self, matrix, t, input_function, **kwargs):
        help_sum = 0
        for j in range(len(matrix)):
            if not kwargs:
                first_part = (input_function(city_list[j], t) * \
                              matrix[j][self.index_city_id]) / city_list[j].population
                second_part = (input_function(self, t) * \
                               matrix[self.index_city_id][j]) / self.population
            else:
                first_part = (input_function(city_list[j], kwargs.get('tau'), t) \
                              * matrix[j][self.index_city_id]) / city_list[j].population
                second_part = (input_function(self, kwargs.get('tau'), t) \
                               * matrix[self.index_city_id][j]) / self.population
            help_sum += first_part - second_part
        if not kwargs:
            return int(round(input_function(self, t) + help_sum, 0))
        else:
            return int(round(input_function(self, kwargs.get('tau'), t), 0))

    # Calculates number of susceptible individuals on day date (14)
    def get_susceptible_mem_local(self, date):
        # TODO implement local time shift
        if date not in self.sus_res:
            if date <= 0:
                self.sus_res[date] = int(round(self.population * fraction_of_susceptible_population, 0))
            else:
                if date - 1 not in self.lat_res:
                    self.lat_res[date - 1] = self.get_latent_mem_local(0, date - 1)
                if date - 1 not in self.sus_res:
                    self.sus_res[date - 1] = self.get_susceptible_mem_local(date - 1)
                self.sus_res[date] = int(round(self.sus_res[date - 1] - self.lat_res[date - 1], 0))
        return self.sus_res[date]

    # Calculates the number of latent individuals on day date who were infected on day date - tau. (15)
    def get_latent_mem_local(self, tau, date):
        # TODO implement local time shift
        if date not in self.lat_res:
            if date <= 0:
                self.lat_res[date] = 0.00001 * self.population
            else:
                if date not in self.sus_res:
                    factor = (fraction_of_susceptible_population *
                              self.get_susceptible_mem_local(date)) / self.population
                else:
                    factor = (fraction_of_susceptible_population * self.sus_res[date]) / self.population
                help_sum = 0
                for i in range(1, length_of_infection_period + 1):
                    if date - i in self.lat_res:
                        help_sum += self.lat_res[date - i] * float(get_infectious_g(i))
                    else:
                        help_sum += self.get_latent_mem_local(tau, date - i) * float(
                                get_infectious_g(i))
                self.lat_res[date] = int(round(factor * help_sum, 0))
        return self.lat_res[date]

    # Calculates the modeled number of of new ill individuals reported to the health registry on day date (16)
    def get_computed_new_sick_individuals_local(self, date):
        # TODO implement local time shift
        help_sum = 0
        latent = {}
        for i in range(0, length_of_incubation_period):
            help_sum += (get_latent_f(i) - get_latent_f(i + 1)) * self.get_latent_mem_local(0, (date - i))
        return round(help_sum * fraction_of_newly_ill_reported, 0)

    def get_latent(self, tau, date):
        if date == first_travel_day_of_latent_individual:
            if self.index_id == City.index_city_id:
                return get_latent_f(tau) * self.get_latent_mem_local(0, date - tau)
            else:
                return 0
        else:
            pass  # TODO implement for rest

    def calculate_first_travel_day(self):
        temp_list = []
        for t in range(forecast_horizon):
            help_sum = 0
            max_sigma = max(airport.city_matrix[self.index_id])
            mu = self.get_latent_mem_local(0, t + 1) / self.get_latent_mem_local(0, t)  # ehh???
            # print(str(t) + ": " + str(mu))
            for tau in range(0, length_of_incubation_period):
                help_sum += get_latent_f(tau) * mu ** (-t)
            temp_list.append((self.get_latent_mem_local(0, t) / self.population) *
                             help_sum * max_sigma)
        # print(temp_list)
        return temp_list.index(min(temp_list))

    def calculate_initial_date_of_epidemic(self):
        # TODO align {ai0(t)} with {bi0(^t)} and count backwards in time to ^t = 0
        self.initial_date_of_epidemic = 0

    # Transport operator Omega.



    # def apply_transport_operator(self, input_function, matrix):
    #     # TODO implement transport operator E. (if apply_transport_operator < 1, then 0.
    #     help_sum = 0
    #     for j in range(len(matrix)):
    #         first_part = input_function * matrix[j][self.index_city_id] / get_population(j)
    #         second_part = input_function * matrix[self.index_city_id][j] / self.population
    #         help_sum += (first_part - second_part)
    #     return input_function + help_sum

    def __str__(self):
        return "ID: " + str(self.index_id) + " \tName: " + self.name + " \t Population: \t" + str(self.population) + \
               " \t x: " + str(self.susceptible) + " \t u: " + str(self.latent) + " \t y: " + str(self.infectious) + \
               " \t z: " + str(self.recovered) + " \t " + str(
                int(self.susceptible + self.infectious + self.latent + self.recovered))


def init_free_parameters(initial_city):
    l = 10
    for k in range(0, l):
        mu = initial_city.get_latent_mem_local(0, )


def get_population(j):
    for city in city_list:
        if city.index_id == j:
            return city.population
    return -1


# Initiate the infection distribution matrix with default values from file
# Row 0 - 4 is tentatively f(t), g(t), h(t), gamma(t) and sigma(t), where t is column index.
def init_distributions():
    with open(infection_distribution_file) as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            infection_distribution.append(row)


def get_infection_distributions(self):
    return self.infection_distribution


def init_city_list():
    with open(city_population_file) as csvfile:
        reader = csv.reader(csvfile)
        index = 0
        for row in reader:
            city_list.append(City(index, row[0], float(row[1])))
            index += 1


def main():
    init_city_list()
    # Algorithm 1: Infection distribution
    init_distributions()

    # Algorithm 2: Local influenza
    index_city = city_list[14]
    City.index_city_id = index_city.index_id

    # Algorithm 3: Estimating free parameters.
    # TODO Implement algorithm 3, estimation of free parameters.

    # Algorithm 4: Initial conditions
    # first_travel_day_of_latent_individual = index_city.calculate_first_travel_day()

    # Algorithm 5: Transport operator. Applied when calculating state equations

    # Algorithm 6: Global influenza.
    index_city.calculate_state_equations_for_day(0, 0)
    # print(index_city)
    for t in range(100):
        index_city.calculate_state_equations_for_day(0, t)
        print(index_city)




    # for i in range(0, 20):
    #     index_city.latent = index_city.get_latent_mem_local(20, i, {}, {})
    #     index_city.susceptible = index_city.get_susceptible_mem_local(i, {}, {})
    #     print(str(i) + " " + str(index_city))
    #     print(index_city.get_computed_new_sick_individuals_local(i))


main()
