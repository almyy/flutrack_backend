import csv

infection_distribution_file = 'C:/Users/mikaelrs/Skole/Master/Repositories/flutrack_backend/' \
                              'prediction/data/infection_distribution.csv'


# Initiate the infection distribution matrix with default values from file
# Row 0 - 4 is tentatively f(t), g(t), h(t), gamma(t) and sigma(t), where t is column index.
def init_distributions():
    infection_distribution = []
    with open(infection_distribution_file) as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            infection_distribution.append(row)
    return infection_distribution
