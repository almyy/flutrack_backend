from prediction import distribute_city_population as dcp
forecast_horizon = 440


def comparison_forecast(city):
    result = []
    t = 0
    counter = 0
    sick_individuals = 0
    while counter < 50:
        if t == 4:
            print(str(counter) + ": " + str(int(sick_individuals * 10 ** (-5))))
            result.append(int(sick_individuals * 0.0001))
            sick_individuals = 0
            t = 0
            counter += 1
        sick_individuals += city.modeled_number_of_new_ill_individuals((4 * counter) + t)

        t += 1

    return result












index_city = dcp.initiate_validation_results()
for t in range(0, 440):
    index_city.get_latent_local(t)
    print(index_city.calculate_state_equations_for_day(t))
comparison_forecast(index_city)
