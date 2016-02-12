# Distributes the city population in four explicit disjoint states,
# Population p = x(t) + sum( u(tau,t),1, tau1) + sum(yi(tau,t),0,tau2) + z(t)
import csv

length_of_incubation_period = 2  # tau1
length_of_infection_period = 8  # tau2
daily_infectious_contact_rate = 0  # lambda #TODO Find a correct lambda value
fraction_of_susceptible_population = 0.99  # alpha #TODO Find a correct alpha value
fraction_of_newly_ill_reported = 0.99  # beta. #TODO Set a correct beta value
infection_distribution = []
city_population = {}
city_population_file = 'C:/Users/mikaelrs/Skole/Master/Repositories/flutrack_backend/' \
                       'prediction/data/citypopulation.csv'
infection_distribution_file = 'C:/Users/mikaelrs/Skole/Master/Repositories/flutrack_backend/' \
                              'prediction/data/infection_distribution.csv'


# return f(time)
def get_latent(time):
    return float(infection_distribution[0][time])


# return g(time)
def get_infectious(time):
    return float(infection_distribution[1][time])


# return h(time)
def get_removed(time):
    return float(infection_distribution[2][time])


class City:
    def __init__(self, index_id, name, population):
        self.index_id = index_id
        self.name = name
        self.population = population
        self.susceptible = self.population * fraction_of_susceptible_population
        self.latent = self.get_latent_mem(0, 0, {}, {})
        self.infectious = 0
        self.recovered = self.population - self.susceptible
        self.initial_date_of_epidemic = 0

    # Initiate the initial conditions for a index cit x_i0
    def initiate_initial_conditions(self):
        # TODO Implement initial conditions
        self.calculate_initial_date_of_epidemic()

        pass

    # Calculates number of susceptible individuals on day date (14)
    def get_susceptible_mem(self, date, sus_results, lat_results):
        # TODO implement local time shift
        if date not in sus_results:
            if date <= 0:
                sus_results[date] = self.population * fraction_of_susceptible_population
            else:
                if date - 1 not in lat_results:
                    lat_results[date - 1] = self.get_latent_mem(0, date - 1, sus_results, lat_results)
                if date - 1 not in sus_results:
                    sus_results[date - 1] = self.get_susceptible_mem(date - 1, sus_results, lat_results)
                sus_results[date] = sus_results[date - 1] - lat_results[date - 1]
        return sus_results[date]

    # Calculates the number of latent individuals on day date who were infected on day date - tau. (15)
    def get_latent_mem(self, tau, date, susceptible, results):
        # TODO implement local time shift
        if date not in results:
            if date <= 0:
                results[date] = 0.00001 * self.population
            else:
                if date not in susceptible:
                    factor = (fraction_of_susceptible_population *
                              self.get_susceptible_mem(date, susceptible, results)) / self.population
                else:
                    factor = (fraction_of_susceptible_population * susceptible[date]) / self.population
                help_sum = 0
                for i in range(1, length_of_infection_period + 1):
                    if date - i in results:
                        help_sum += results[date - i] * float(get_infectious(i))
                    else:
                        help_sum += self.get_latent_mem(tau, date - i, susceptible, results) * float(get_infectious(i))
                results[date] = round(factor * help_sum, 0)
        return results[date]

    # Calculates the modeled number of of new ill individuals reported to the health registry on day date (16)
    def get_computed_new_sick_individuals(self, date):
        # TODO implement local time shift
        help_sum = 0
        latent = {}
        for i in range(0, length_of_incubation_period):
            help_sum += (get_latent(i) - get_latent(i + 1)) * self.get_latent_mem(0, (date - i), {}, latent)
        return round(help_sum * fraction_of_newly_ill_reported, 0)

    def calculate_initial_date_of_epidemic(self):
        # TODO align {ai0(t)} with {bi0(^t)} and count backwards in time to ^t = 0
        #  return the corresponding t, as initial date of epidemic

        self.initial_date_of_epidemic = 0

    def __str__(self):
        return "ID:\t " + str(self.index_id) + " Name: \t" + self.name + " \t Population: \t" + str(self.population) + \
               " \t x: " + str(self.susceptible) + " \t u: " + str(self.latent) + " \t y: " + str(self.infectious) + \
               " \t z: " + str(self.recovered) + " \t " + str(
                self.susceptible + self.infectious + self.latent + self.recovered)


# Initiate the infection distribution matrix with default values from file
# Row 0 - 4 is tentatively f(t), g(t), h(t), gamma(t) and sigma(t), where t is column index.
def init_distributions():
    with open(infection_distribution_file) as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            infection_distribution.append(row)


def get_infection_distributions(self):
    return self.infection_distribution


def init_city_population_list():
    with open(city_population_file) as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            city_population[row[0]] = row[1]


def main():
    init_city_population_list()
    # Algorithm 1
    init_distributions()
    # Algorithm 2
    index_city = City(10, "Hong Kong", float(city_population["Hong Kong"]))
    # Algorithm 3: Estimating free parameters.

    # for i in range(0, 20):
    #     index_city.latent = index_city.get_latent_mem(20, i, {}, {})
    #     index_city.susceptible = index_city.get_susceptible_mem(i, {}, {})
    #     print(str(i) + " " + str(index_city))
    #     print(index_city.get_computed_new_sick_individuals(i))


main()
