from prediction import distribute_city_population as dcp

forecast_horizon = 300


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
            tmp_res = 0
    return result


def get_peak_day_results():
    for city in dcp.city_list:
        comparison_forecast(city)
    sort_list = sorted(dcp.city_list, key=lambda l: (l.peak_day, l.name))
    return sort_list

for attempt in range(0, 1):
    index_city = dcp.initiate_validation_results(15)
    for t in range(0, forecast_horizon):
        dcp.calculate_state_equations(t)
    plot = get_peak_day_results()
    result_matrix = []
    for city in reversed(plot):
        row = [city.id, str(city.name), comparison_forecast(city)]
        result_matrix.append(row)
    s = [[str(e) for e in row] for row in result_matrix]
    lens = [max(map(len, col)) for col in zip(*s)]
    fmt = '\t'.join('{{:{}}}'.format(x) for x in lens)
    table = [fmt.format(*row) for row in s]
    print('\n'.join(table))
    print(str(attempt) + ": " + str(dcp.city_list[attempt]))

