# Distributes the city population in four explicit disjoint states,
# Population p = x(t) + sum( u(tau,t),1, tau1) + sum(yi(tau,t),0,tau2) + z(t)
import csv
import matplotlib.pyplot as plt
from prediction import airport
from prediction import distribution_initiation as di

city_matrix = airport.city_matrix
length_of_incubation_period = 2  # tau1
length_of_infection_period = 8  # tau2
daily_infectious_contact_rate = 1  # lambda #TODO Find a correct lambda value
fraction_of_susceptible_population = 0.641  # alpha #TODO Find a correct alpha value
fraction_of_newly_ill_reported = 0.99  # beta. #TODO Set a correct beta value
infection_distribution = di.init_distributions
city_list = di.init_city_list()
city_population_file = 'C:/Users/mikaelrs/Skole/Master/Repositories/flutrack_backend/' \
                       'prediction/data/citypopulation.csv'
infection_distribution_file = 'C:/Users/mikaelrs/Skole/Master/Repositories/flutrack_backend/' \
                              'prediction/data/infection_distribution.csv'
first_travel_day_of_latent_individual = 1
forecast_horizon = 440


# Initiate the infection distribution matrix with default values from file
# Row 0 - 4 is tentatively f(t), g(t), h(t), gamma(t) and sigma(t), where t is column index.
def init_distributions():
    with open(infection_distribution_file) as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            infection_distribution.append(row)


def init_city_list():
    with open(city_population_file) as csvfile:
        reader = csv.reader(csvfile)
        index = 0
        for row in reader:
            city_list.append(City(index, row[0], float(row[1])))
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


class City:
    index_city_id = 0

    def __init__(self, index_id, name, population):
        self.index_id = index_id
        self.name = name
        self.population = int(population)
        self.susceptible = 0
        self.latent = 0
        self.infectious = 0
        self.recovered = 0
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
        self.susceptible = self.get_susceptible(t)
        inf = 0
        lat = 0
        for tau in range(0, length_of_infection_period + 1):
            if tau <= length_of_incubation_period:
                lat += self.get_latent(tau, t)
            inf += self.get_infectious(tau, t)
        self.latent = lat
        self.infectious = inf
        self.recovered = self.population - (self.susceptible + lat + inf)

    # Transport operator omega for the travel matrix (8)
    def apply_transport_operator(self, t, input_function, **kwargs):
        help_sum = 0
        for j in range(len(city_matrix)):
            if not kwargs:
                first_part = (input_function(city_list[j], t) * city_matrix[j][self.index_city_id]) / city_list[
                    j].population
                second_part = (input_function(self, t) * city_matrix[self.index_city_id][j]) / self.population
            else:
                first_part = (input_function(city_list[j], kwargs.get('tau'), t) * city_matrix[j][self.index_city_id]) / \
                             city_list[j].population
                second_part = (input_function(self, kwargs.get('tau'), t) * city_matrix[self.index_city_id][
                    j]) / self.population
            help_sum += first_part - second_part
        if not kwargs:
            return int(round(input_function(self, t) + help_sum, 0))
        else:
            return int(round(input_function(self, kwargs.get('tau'), t), 0))

    # Returns the number of susceptible individuals for day t (9).
    def get_susceptible(self, t, **kwargs):
        if t not in self.sus_res:
            if t <= 0:
                self.sus_res[t] = int(round(self.population * fraction_of_susceptible_population))
            else:
                if (0, t - 1) not in self.lat_res:
                    if kwargs.get('local'):
                        self.lat_res[0, t - 1] = int(round(self.get_latent_local(0, t - 1)))
                    else:
                        self.lat_res[0, t - 1] = int(round(self.get_latent(0, t - 1)))
                if t - 1 not in self.sus_res:
                    self.sus_res[t - 1] = int(round(self.get_susceptible(t - 1)))
                self.sus_res[t] = self.sus_res[t - 1] - self.lat_res[0, t - 1]
        return self.sus_res[t]

    # Calculates the number of latent individuals on day date who were infected on day date - tau. (15)
    def get_latent_local(self, tau, t):
        # TODO implement local time shift
        if (tau, t) not in self.lat_res:
            if t <= 0:
                self.lat_res[tau, t] = int(round(0.00001 * self.population, 0))
            else:
                if t not in self.sus_res:
                    factor = (fraction_of_susceptible_population * self.get_susceptible(t, local=True)) / self.population
                else:
                    factor = (fraction_of_susceptible_population * self.sus_res[t]) / self.population
                help_sum = 0
                for i in range(1, length_of_infection_period + 1):
                    if (tau, t - i) in self.lat_res:
                        help_sum += self.lat_res[tau, t - i] * get_infectious_g(i)
                    else:
                        help_sum += self.get_latent_local(tau, t - i) * get_infectious_g(i)
                self.lat_res[tau, t] = int(round(factor * help_sum, 0))
        return self.lat_res[tau, t]

    # Returns the number of infectious individuals on day t who where infected on day t-tau (10)
    def get_latent(self, tau, t):
        if length_of_incubation_period >= tau >= 0:
            if (tau, t) not in self.lat_res:
                if tau == 0:
                    factor = daily_infectious_contact_rate * self.get_susceptible(t, local=False) / self.population
                    help_sum = 0
                    for i in range(1, length_of_infection_period):
                        if (tau, t - i) in self.lat_res:
                            help_sum += self.lat_res[tau, t - i] * get_infectious_g(i)
                    self.lat_res[0, t] = int(round(factor * help_sum, 0))
                else:
                    part_one = (1 - latent_becomes_infectious(tau - 1))
                    part_two = self.apply_transport_operator(t - 1, City.get_latent, tau=(tau - 1))
                    self.lat_res[tau, t] = int(round(part_one * part_two, 0))
        else:
            return -1
        return self.lat_res[tau, t]

    # Returns the number of infectious individuals who were infected on day t - tau (11)
    def get_infectious(self, tau, t):
        if tau <= 0:
            return 0
        elif tau <= length_of_incubation_period:
            part_one = latent_becomes_infectious(tau - 1) * self.apply_transport_operator(t - 1, City.get_latent,
                                                                                          tau=(tau - 1))
            part_two = (1 - infectious_recovers(tau - 1)) * self.get_infectious(tau - 1, t - 1)
            return int(round(part_one + part_two, 0))
        elif tau <= length_of_infection_period - 1:
            return int(round((1 - infectious_recovers(tau)) * self.get_infectious(tau - 1, t - 1), 0))
        return 0

    # Number of individuals who became ill on day t. (12)
    def calculate_daily_morbidity(self, t):
        result = 0
        for tau in range(0, length_of_incubation_period):
            result += latent_becomes_infectious(tau) * self.apply_transport_operator(t, City.get_latent, tau=tau)
        return result

    # Modeled number of new ill individuals reported to the health registry. (13)
    def modeled_number_of_new_ill_individuals(self, t):
        return int(round(fraction_of_newly_ill_reported * self.calculate_daily_morbidity(t), 0))

    # Calculates the modeled number of of new ill individuals reported to the health registry on day date (16)
    def get_computed_new_sick_individuals_local(self, date):
        # TODO implement local time shift
        help_sum = 0
        for i in range(0, length_of_incubation_period):
            help_sum += (get_latent_f(i) - get_latent_f(i + 1)) * self.get_latent(0, (date - i))
        return round(help_sum * fraction_of_newly_ill_reported, 0)

    def calculate_recovered(self, t):
        inf = 0
        lat = 0
        for tau in range(0, length_of_infection_period + 1):
            if tau <= length_of_incubation_period:
                lat += self.get_latent(tau, t)
            inf += self.get_infectious(tau, t)
        return self.population - (self.susceptible + lat + inf)

    def calculate_first_travel_day(self):
        temp_list = []
        for t in range(forecast_horizon):
            help_sum = 0
            max_sigma = max(airport.city_matrix[self.index_id])
            mu = self.get_latent_local(0, t + 1) / self.get_latent_local(0, t)  # ehh???
            print(str(t) + ": " + str(mu))
            for tau in range(0, length_of_incubation_period):
                help_sum += get_latent_f(tau) * mu ** (-t)
            temp_list.append((self.get_latent_local(0, t) / self.population) * help_sum * max_sigma)
        return temp_list.index(min(temp_list))

    def calculate_initial_date_of_epidemic(self):
        # TODO align {ai0(t)} with {bi0(^t)} and count backwards in time to ^t = 0
        self.initial_date_of_epidemic = 0

    # Calculates the population by adding all of the disjoint states according to equation (1)
    def calculate_city_population(self, t):
        sum_susceptible = self.get_susceptible(t)
        sum_recovered = self.recovered
        sum_latent = 0
        sum_infectious = 0
        for tau in range(0, length_of_infection_period + 1):
            if tau <= length_of_incubation_period:
                sum_latent += self.get_latent(tau, t)
            sum_infectious += self.get_infectious(tau, t)
        return int(sum_susceptible + sum_latent + sum_infectious + sum_recovered)

    def __str__(self):
        return "ID: " + str(self.index_id) + " \tName: " + self.name + " \t Population: \t" + str(self.population) + \
               " \t x: " + str(self.susceptible) + " \t u: " + str(self.latent) + "     \t y: " + str(self.infectious) + \
               " \t z: " + str(self.recovered)


def main():
    # init_city_list()
    # Algorithm 1: Infection distribution DONE
    # init_distributions()

    # Algorithm 2: Local influenza
    index_city = city_list[14]
    City.index_city_id = index_city.index_id
    # Algorithm 3: Estimating free parameters.
    # TODO Implement algorithm 3, estimation of free parameters.

    # Algorithm 4: Initial conditions
    # first_travel_day_of_latent_individual = index_city.calculate_first_travel_day()

    # Algorithm 5: Transport operator. Applied when calculating state equations DONE.

    # Algorithm 6: Global influenza. Calculate state-equations. DONE

    latent_per_day = []
    susceptible_per_day = []
    infectious_per_day = []
    latent = []
    recovered = []
    all_lat = 0
    sum_population = []
    index_city.get_latent_local(0, 2)
    for t in range(100):
        index_city.calculate_state_equations_for_day(0, t)
        sum_population.append(index_city.calculate_city_population(t))
        lat = 0
        inf = 0
        for i in range(0, length_of_infection_period + 1):
            if i < length_of_incubation_period:
                lat += index_city.get_latent(i, t)
            inf += index_city.get_infectious(i, t)
        infectious_per_day.append(inf)
        all_lat += index_city.latent
        latent.append(all_lat)
        recovered.append(index_city.recovered)
        latent_per_day.append(lat)
        susceptible_per_day.append(index_city.susceptible)
        print(str(t) + " \t" + str(index_city) + " \t Expected pop: " + str(index_city.calculate_city_population(t)))

        # plt.plot(latent_per_day, label='Latent')
        # plt.plot(susceptible_per_day, label='Susceptible')
        # plt.plot(infectious_per_day, label='Infectious')
        # # plt.plot(latent, label='Sum of latent')
        # plt.plot(recovered, label='Recovered')
        # plt.plot(sum_population, label='Calculated population')
        # plt.legend(loc=2)
        # plt.show()


main()
