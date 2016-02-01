import unittest


class TestAirportMethods(unittest.TestCase):
    def setUp(self):
        self.city_names = airport.init_city_names('cities.txt')


class InitializingCityNamesTestCase(TestAirportMethods):
    def test_city_names(self):
        size = len(self.city_names)
        self.assertEqual(size, 52)

suite = unittest.TestLoader().loadTestsFromTestCase(InitializingCityNamesTestCase)
unittest.TextTestRunner(verbosity=2).run(suite)