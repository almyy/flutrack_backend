from prediction import distribute_city_population as dcp

forecast_horizon = 440


def comparison_forecast(city):
    result = []
    tmp_res = 0
    for t in range(0, forecast_horizon):
        tmp_res += int(city.get_daily_computed_morbidity(t + 1) * 0.001)
        if t % 4 == 0:
            if 0 < tmp_res < 10:
                result.append('*')
            elif 10 <= tmp_res <= 100:
                result.append('-')
            elif tmp_res > 100:
                result.append('+')
            else:
                result.append(' ')
            tmp_res = 0
    return result


index_city = dcp.initiate_validation_results()
for t in range(0, forecast_horizon):
    dcp.calculate_state_equations(t)

result_matrix = []
for city in dcp.city_list:
    row = [str(city.index_id), str(city.name), comparison_forecast(city)]
    result_matrix.append(row)
    # result_matrix.append(comparison_forecast(city))

# print(result_matrix)
s = [[str(e)for e in row] for row in result_matrix]
lens = [max(map(len, col)) for col in zip(*s)]
fmt = '\t'.join('{{:{}}}'.format(x) for x in lens)
table = [fmt.format(*row) for row in s]
var = ['July', 'Aug', 'Sept', 'Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'March', 'April', 'May', 'June', 'July', 'Aug',
       'Sept']
print(var)
print('\n'.join(table))
