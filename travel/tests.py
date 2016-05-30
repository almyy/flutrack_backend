import os
import unittest
import manage_air_traffic as apm

class AirportTestCase(unittest.TestCase):
    def setUp(self):
        self.city_dictionary = apm.init_city_dictionary()
        self.city_names = apm.city_list
        self.travel_matrix = apm.get_transportation_matrix()
        self.passengers_lax_jfk = 1440618
        self.passengers_jfk_lax = 1417826
        self.passengers_lga_lax = 4380
        self.passengers_lax_lga = 3222

    def test_size_of_city_list_and_matrix(self):
        size = len(self.city_names)
        row_size = len(self.travel_matrix)
        col_size = len(self.travel_matrix[0])
        self.assertEqual(size, row_size, "Wrong size of city list")
        self.assertEqual(row_size, col_size, "Matrix not symmetrical")

    def test_travel_matrix_calculates_correctly(self):
        la_index = self.city_names.index('Los Angeles')
        ny_index = self.city_names.index('New York')
        travelers_between_new_york_and_los_angeles = self.travel_matrix[la_index][ny_index]
        travelers_between_los_angeles_and_new_york = self.travel_matrix[ny_index][la_index]
        expected_travelers = int((self.passengers_lax_lga + self.passengers_lax_jfk + self.passengers_jfk_lax + self.passengers_lga_lax) / 365)

        self.assertEqual(travelers_between_los_angeles_and_new_york, travelers_between_new_york_and_los_angeles,
                         "The matrix is not symmetric")
        self.assertEqual(travelers_between_new_york_and_los_angeles, expected_travelers,
                         "Wrong calculated daily travelers")

suite = unittest.TestLoader().loadTestsFromTestCase(AirportTestCase)
unittest.TextTestRunner(verbosity=2).run(suite)
