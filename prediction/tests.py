import unittest

from airport import airport
from prediction import distribute_city_population as dcp




class DistributionTestCase(unittest.TestCase):
    def setUp(self):
        self.tau1 = dcp.length_of_incubation_period
        self.tau2 = dcp.length_of_infection_period
        self.llambda = dcp.daily_infectious_contact_rate
        self.alpha = dcp.fraction_of_susceptible_population
        self.beta = dcp.fraction_of_newly_ill_reported

    def test_correct_values_of_parameters(self):
        self.assertEqual(self.tau1, 2, "Wrong value for tau1, incubation period.")
        self.assertEqual(self.tau2, 8, "Wrong value for tau2, infection period.")

    def test_initial_conditions_in_initial_city(self):
        result = True
        for city in dcp.city_list:
            if city.get_latent(0, 0) != 0:
                result = False
        self.assertEqual(True, result)

    def test_latent_state_distribution_ft(self):
        self.assertEqual(dcp.get_latent_f(1), 0.70)
        self.assertEqual(dcp.get_latent_f(2), 0.20)
        self.assertEqual(dcp.get_latent_f(3), 0.00)
        self.assertEqual(dcp.get_latent_f(4), 0.00)

    def test_infectious_state_distribution_gt(self):
        self.assertEqual(dcp.get_infectious_g(2), 0.77)
        self.assertEqual(dcp.get_infectious_g(3), 0.82)
        self.assertEqual(dcp.get_infectious_g(4), 0.54)
        self.assertEqual(dcp.get_infectious_g(5), 0.30)

    def test_removed_state_distribution_ht(self):
        self.assertEqual(dcp.get_removed_h(2), 0.03)
        self.assertEqual(dcp.get_removed_h(3), 0.18)
        self.assertEqual(dcp.get_removed_h(4), 0.46)
        self.assertEqual(dcp.get_removed_h(5), 0.70)

    def test_estimation_of_free_parameters(self):
        expected_alpha = 0.641
        expected_lambda = 1.055
        self.assertEqual(self.alpha, expected_alpha)
        self.assertEqual(self.llambda, expected_lambda)

    def test_local_influenza_spread(self):
        pass

    def test_calculation_of_state_equations(self):
        hong_kong = dcp.city_list[9]
        self.assertEqual(hong_kong.name, "Hong Kong", "Wrong city.")

        expected_susceptible = hong_kong.population * self.alpha
        expected_latent = 73
        expected_infectious = 128
        expected_recovered = hong_kong.population - expected_susceptible - expected_latent - expected_infectious

        dcp.initiate_initial_conditions(0)
        hong_kong.calculate_state_equations_for_day(0)
        self.assertEqual(hong_kong.susceptible, expected_susceptible, "Unexpected susceptible population.")
        self.assertEqual(hong_kong.latent, expected_latent, "Unexpected latent population.")
        self.assertEqual(hong_kong.infectious, expected_infectious, "Unexpected infectious population.")
        self.assertEqual(hong_kong.recovered, expected_recovered, "Unexpected recovered population.")

    def test_disjoint_states(self):
        hong_kong = dcp.city_list[9]
        self.assertEqual(hong_kong.name, 'Hong Kong', "Wrong city")
        hong_kong.calculate_state_equations_for_day(0)
        self.assertEqual(hong_kong.population, hong_kong.calculate_city_population(), "Population does not match1")
        hong_kong.calculate_state_equations_for_day(1)
        self.assertEqual(hong_kong.population, hong_kong.calculate_city_population(), "Population does not match2")
        hong_kong.calculate_state_equations_for_day(1)
        self.assertEqual(hong_kong.population, hong_kong.calculate_city_population(), "Population does not match3")
        hong_kong.calculate_state_equations_for_day(5)
        self.assertEqual(hong_kong.population, hong_kong.calculate_city_population(), "Population does not match4")
        hong_kong.calculate_state_equations_for_day(5)
        self.assertEqual(hong_kong.population, hong_kong.calculate_city_population(), "Population does not match5")


suite = unittest.TestLoader().loadTestsFromTestCase(DistributionTestCase)
unittest.TextTestRunner(verbosity=2).run(suite)
