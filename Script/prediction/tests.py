import unittest
from Script.prediction import airport
from Script.prediction import distribute_city_population


class AirportTestCase(unittest.TestCase):
    def setUp(self):
        self.city_names = airport.city_list
        self.city_dictionary = airport.init_city_dictionary()
        self.city_matrix = airport.city_matrix
        self.passengers_lax_jfk = 996370
        self.passengers_jfk_lax = 986385
        self.passengers_lga_lax = 3850
        self.passengers_lax_lga = 2602

    def test_size_of_city_list(self):
        size = len(self.city_names)
        self.assertEqual(size, 52, "Wrong size of city list")

    def test_size_of_matrix(self):
        row_size = len(self.city_matrix)
        col_size = len(self.city_matrix[0])
        self.assertEqual(row_size * col_size, 52 * 52, "Wrong matrix size")

    def test_reading_air_travel_data(self):
        # air_travel_data = airport.read_air_travel_data()
        passengers_lax_jfk = 0
        passengers_lax_lga = 0
        passengers_jfk_lax = 0
        passengers_lga_lax = 0

        for row in airport.read_air_travel_data():
            if row[0] == 'LAX' and row[1] == 'JFK':
                passengers_lax_jfk = row[2]
            if row[0] == 'LAX' and row[1] == 'LGA':
                passengers_lax_lga = row[2]
            if row[0] == 'JFK' and row[1] == 'LAX':
                passengers_jfk_lax = row[2]
            if row[0] == 'LGA' and row[1] == 'LAX':
                passengers_lga_lax = row[2]

        self.assertEqual(passengers_lax_jfk, self.passengers_lax_jfk,
                         "Wrong passenger number for flights from LAX to JFK")
        self.assertEqual(passengers_lax_lga, self.passengers_lax_lga,
                         "Wrong passenger number for flights from LAX to LGA")
        self.assertEqual(passengers_jfk_lax, self.passengers_jfk_lax,
                         "Wrong passenger number for flights from JFK to LAX")
        self.assertEqual(passengers_lga_lax, self.passengers_lga_lax,
                         "Wrong passenger number for flights from LGA to LAX")

    def test_mapping_airports_to_cities(self):
        airports = airport.map_airports_to_cities(self.city_dictionary, airport.get_flight_data_local())
        new_york_airports = ['JFK', 'JRB', 'TSS', 'LGA']
        correctly_mapped = True
        for key in new_york_airports:
            if key not in airports["New York"]:
                correctly_mapped = False

        self.assertEqual(True, correctly_mapped, "Airport not in new york airports")
        self.assertEqual(len(airports["New York"]), len(new_york_airports), "Wrong length of airport list for New York")

    def test_initiation_of_transportation_matrix(self):
        passengers_between_la_ny = self.passengers_lax_jfk + self.passengers_jfk_lax + self.passengers_lga_lax \
                                   + self.passengers_lax_lga

        self.assertEqual(airport.get_passengers_between_cities("Los Angeles", "New York"), passengers_between_la_ny,
                         "Wrong passenger count between LA and NYC")


class DistributionTestCase(unittest.TestCase):
    def setUp(self):
        self.tau1 = distribute_city_population.length_of_incubation_period
        self.tau2 = distribute_city_population.length_of_infection_period
        self.llambda = distribute_city_population.daily_infectious_contact_rate
        self.alpha = distribute_city_population.fraction_of_susceptible_population
        self.beta = distribute_city_population.fraction_of_newly_ill_reported

    def test_correct_values_of_parameters(self):
        self.assertEqual(self.tau1, 2, "Wrong value for tau1, incubation period.")
        self.assertEqual(self.tau2, 8, "Wrong value for tau2, infection period.")

    def test_initial_conditions_in_initial_city(self):
        self.assertEqual(False, True)

    def test_latent_state_distribution_ft(self):
        self.assertEqual(distribute_city_population.get_latent(1), 0.70)
        self.assertEqual(distribute_city_population.get_latent(2), 0.20)
        self.assertEqual(distribute_city_population.get_latent(3), 0.00)
        self.assertEqual(distribute_city_population.get_latent(4), 0.00)

    def test_infectious_state_distribution_gt(self):
        self.assertEqual(distribute_city_population.get_infectious(2), 0.77)
        self.assertEqual(distribute_city_population.get_infectious(3), 0.82)
        self.assertEqual(distribute_city_population.get_infectious(4), 0.54)
        self.assertEqual(distribute_city_population.get_infectious(5), 0.30)

    def test_removed_state_distribution_ht(self):
        self.assertEqual(distribute_city_population.get_removed(2), 0.03)
        self.assertEqual(distribute_city_population.get_removed(3), 0.18)
        self.assertEqual(distribute_city_population.get_removed(4), 0.46)
        self.assertEqual(distribute_city_population.get_removed(5), 0.70)

    def test_estimation_of_free_parameters(self):
        expected_alpha = 69
        expected_lambda = 69
        self.assertEqual(self.alpha, expected_alpha)
        self.assertEqual(self.llambda, expected_lambda)


suite = unittest.TestLoader().loadTestsFromTestCase(AirportTestCase)
unittest.TextTestRunner(verbosity=2).run(suite)
suite = unittest.TestLoader().loadTestsFromTestCase(DistributionTestCase)
unittest.TextTestRunner(verbosity=2).run(suite)
