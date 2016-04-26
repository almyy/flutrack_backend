from prediction import distribute_city_population as dcp
import matplotlib.pyplot as plt

import plotly
from plotly.graph_objs import Scatter, Layout

forecast_horizon = 440 + 44


def comparison_forecast(city):
    result = []
    tmp_res = 0
    city.peak_day = city.daily_morbidity.index(max(city.daily_morbidity))
    for t in range(0, forecast_horizon):
        morbidity = city.daily_morbidity[t]
        tmp_res += int(morbidity / (city.population / 100000))
        if t % 4 == 0:
            if 0 < tmp_res < 10:
                result.append('*')
            elif 10 <= tmp_res <= 100:
                result.append('-')
            elif tmp_res > 100:
                result.append('+')
            else:
                result.append(' ')
            # result.append(tmp_res)
            tmp_res = 0
    return result


def get_peak_day_results():
    for city in dcp.city_list:
        comparison_forecast(city)
    sort_list = sorted(dcp.city_list, key=lambda l: (l.peak_day, l.name))
    return sort_list


index_city = dcp.initiate_validation_results()
for t in range(0, forecast_horizon):
    dcp.calculate_state_equations(t)

plot = get_peak_day_results()
points = []
label = []

# for city in plot:
#     points.append(city.peak_day)
#     label.append(city.name)

grais_data_labels = ['Hong Kong', 'Manilla', 'Singapore', 'Jakrata', 'Bangkok', 'Honolulu', 'Madras', 'Bombay', 'Dehli',
                     'San Francisco', 'Tokyo', 'London', 'Los Angeles', 'Teheran', 'Atlanta',
                     'Kolkata', 'karachi', 'Washington', 'Chicago', 'Houston', 'New York', 'Stockholm', 'Paris',
                     'Montreal', 'Madrid',
                     'Rome', 'Seoul', 'Berlin', 'Warsaw', 'Cairo', 'Mexico City', 'Beijing',
                     'Shanghai', 'Lagos', 'Casablanca', 'Caracas', 'Lima', 'Caracas' 'Budapest', 'Havana', 'Sofia',
                     'Bogota', 'Kinshasa',
                     'Sao Paulo', 'Johannesburg', 'Buenos Aires', 'Capetown', 'Sydney', 'Santaigo', 'Melbourne',
                     'Perth', 'Wellington']

grais_data = [0, 4, 15, 35, 62, 65, 81, 83, 112, 115, 121, 121, 125, 130, 130, 135, 137, 138, 140, 140, 145, 145, 150,
              160,
              160, 160, 163, 167, 172, 172, 175, 175, 180, 180, 190, 190, 195, 197, 200, 202, 210, 210, 213, 218, 218,
              285, 287, 300, 340, 340, 360, 360]

# for p in points:
#     print(p)
#
# for label in label:
#     print(label)
# plotly.offline.plot({
#     "data": [
#         Scatter(x=grais_data, y=grais_data_labels, mode='lines+markers', name="Grais et al."),
#         # Scatter(x=points, y=label, name="Our results")
#     ],
#     "layout": Layout(
#             title="Temporal progression of forecast"
#     )
# })




result_matrix = []
for city in reversed(plot):
    row = [city.id, str(city.name), comparison_forecast(city)]
    result_matrix.append(row)
    result_matrix.append(comparison_forecast(city))
    # print(str(city.name) + " \t\t" + str(city.peak_day))
#
# for city in sort_list:
#     print(str(city.index_id) + " Peak day: " + str(city.peak_day))

# print(result_matrix)
s = [[str(e) for e in row] for row in result_matrix]
lens = [max(map(len, col)) for col in zip(*s)]
fmt = '\t'.join('{{:{}}}'.format(x) for x in lens)
table = [fmt.format(*row) for row in s]
var = ['July', 'Aug', 'Sept', 'Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'March', 'April', 'May', 'June', 'July', 'Aug',
       'Sept']
print(var)
print('\n'.join(table))
