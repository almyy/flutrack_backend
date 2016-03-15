import csv
import os

infection_distribution_file = os.path.abspath(os.path.dirname(__file__)) + 'data/infection_distribution.csv'


# Initiate the infection distribution matrix with default values from file
# Row 0 - 4 is tentatively f(t), g(t), h(t), gamma(t) and sigma(t), where t is column index.
def init_distributions():
    infection_distribution = []
    with open(infection_distribution_file) as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            infection_distribution.append(row)
    return infection_distribution
