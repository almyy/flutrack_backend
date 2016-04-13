import unittest


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
        passengers_between_la_ny = self.passengers_lax_jfk + self.passengers_jfk_lax + self.passengers_lga_lax + self.passengers_lax_lga
        self.assertEqual(airport.get_passengers_between_cities("Los Angeles", "New York"), passengers_between_la_ny,
                         "Wrong passenger count between LA and NYC")
