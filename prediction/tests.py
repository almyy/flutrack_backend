import unittest

from prediction import distribute_city_population as dcp


class DistributionTestCase(unittest.TestCase):
    def setUp(self):
        self.tau1 = dcp.length_of_incubation_period
        self.tau2 = dcp.length_of_infection_period
        self.llambda = dcp.daily_infectious_cr
        self.alpha = dcp.fraction_of_susceptible_population
        self.beta = dcp.fraction_of_newly_ill_reported

    def test_correct_values_of_parameters(self):
        self.assertEqual(self.tau1, 2, "Wrong value for tau1, incubation period.")
        self.assertEqual(self.tau2, 8, "Wrong value for tau2, infection period.")

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


suite = unittest.TestLoader().loadTestsFromTestCase(DistributionTestCase)
unittest.TextTestRunner(verbosity=2).run(suite)
