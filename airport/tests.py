import unittest
import airport as apm


class AirportTestCase(unittest.TestCase):
    def setUp(self):
        self.city_names = apm.city_list
        self.city_dictionary = apm.init_city_dictionary()
        self.travel_matrix = apm.get_travel_matrix()
        self.passengers_lax_jfk = 996370
        self.passengers_jfk_lax = 986385
        self.passengers_lga_lax = 3850
        self.passengers_lax_lga = 2602

    def test_size_of_city_list(self):
        size = len(self.city_names)
        self.assertEqual(size, 52, "Wrong size of city list")

    def test_size_of_matrix(self):
        row_size = len(self.travel_matrix)
        col_size = len(self.travel_matrix[0])
        self.assertEqual(row_size * col_size, 52 * 52, "Wrong matrix size")

    def test_reading_air_travel_data(self):
        passengers_lax_jfk = 0
        passengers_lax_lga = 0
        passengers_jfk_lax = 0
        passengers_lga_lax = 0

        for row in apm.read_air_travel_data():
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
        airports = apm.map_airports_to_cities(self.city_dictionary, apm.get_flight_data_local())

        new_york_airports = ['JFK', 'JRB', 'TSS', 'LGA']
        los_angeles_airports = ['LAX']
        cairo_airports = ['CAI']

        correctly_mapped_ny = self.check_airports(airports["New York"], new_york_airports)
        correctly_mapped_la = self.check_airports(airports["Los Angeles"], los_angeles_airports)
        correctly_mapped_cairo = self.check_airports(airports["Cairo"], cairo_airports)


        self.assertEqual(True, correctly_mapped_ny, "Airport not in New York airports")
        self.assertEqual(True, correctly_mapped_la, "Airport not in Los Angeles airports")
        self.assertEqual(True, correctly_mapped_cairo, "Airport not in Cairo airports")

    def check_airports(self, test_set, correct_set):
        if len(test_set) != len(correct_set):
            return False
        for key in correct_set:
            if key not in test_set:
                return False
        return True


suite = unittest.TestLoader().loadTestsFromTestCase(AirportTestCase)
unittest.TextTestRunner(verbosity=2).run(suite)
