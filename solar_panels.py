def power_output_per_area(poa_act, temp_act, power_rated, poa_ref=1000, temp_ref=25, temp_coef=0.35, correction=1):

    power_output_per_area = power_rated * (poa_act/poa_ref) * (1 + temp_coef*(temp_act-temp_ref)) * correction

    return power_output_per_area


def power_output_array():
    return


# number of panels 1 - area_roof/area_panel
# peak power of panels 320 - 465
# orientation theta -90 - 90
# tilt angle 0 - 40
# inverter peak power 1500 - 25000

