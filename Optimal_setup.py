""" We need to find the best investment option for a solarpanel setup. As a first step, we search for the maximal gain after the
lifetime of the panels. The variables are the angle for the panels, the number of installed panels, the type of panel, the type
of convertor. The input is the solar irradiance, the orientation of the roof, the electricity consumption. The output of the solar
panels is limited by the maximum power flow of the convertor, as well as the available area."""

'''Import'''
# Importing some libraries and help files
import pandas as p
import solar_angles as sa
from matplotlib import pyplot
import main

# Importing some excel files as data frames
solar_data_file = main.df_irr                                       # Contains corrigated irradiance and panel temperature
load_profile = p.read_excel('Load_profile.xlsx',sheet_name=0)       # Contains load profile of the house in 2018 [kW]
load_profile = load_profile.set_index('Time')                       # Sets index to time
invertor_data_file = p.read_excel('INV EXCEL.xlsx',sheet_name=0)    # Contains price, efficiency and maximum DC power of invertors
invertor_data_file = invertor_data_file.set_index('REFERENCE')      # Sets index to provided reference number in excel file
panel_file = p.read_excel('Solar_panel_data.xlsx',sheet_name=0)     # Contains all relevant solar panel parameters
panel_file = panel_file.set_index('PANELS')                         # Sets index to provided reference number in excel file

'''Irradiance parameters'''
# All angles are given in degrees, only internally in functions, they are converted to radians for calculations
initial_data_loading = False
generate_plots = True
year = 2018

longitude = 5.5
latitude = 51
time_zone = 1
btw_panels = 0.21

# Panel orientation parameters
tilt_angle = 0
orientation_angle = 0  # the direction that a solar panel faces, expressed in degrees clockwise from north.

'''Economic parameters'''
capacity_tarif = 37.65           # in case of digital [€/kW]
inflation_rate = 0.027           # Concerns the procentual evolution of prices of electricty and invertor costs
p_op_start = 0.10604             # Price you get for energy you send to the grid in case of a digital meter [€/kWh]
p_van_start_digital = 0.315      # Price for electricity in case of a digital meter
p_van_start_classic = 0.337      # Price for electricity in case of an analog meter
cost_per_year_digital = 78.04    # Fixed cost per year [€/yr]
cost_per_year_classic = 172.17   # Fixed cost per year [€/yr]
prosument_tarif_inv = 41.11      # Cost per kW installed invertor in case of an analog meter [€/kW]
heffingen_start = 0.01646        # Heffingen [€/kWh]
btw_panels = 0.21           
installation = 0.88               # Total investment =  cost equipment * (1+installation) 
cable_losses = 0.02              
dust_losses = 0.04

'''How to plot'''
#plot1 = pyplot.plot(untouched_gains.index, untouched_gains.values)
#pyplot.show()

'''Functions to get solar panel parameters from the solar panel file'''
# Get peakpower of a solar panel [kWp]
def peakpower(n):
    return panel_file['Piekvermogen'][n]

# Get efficiency of a solar panel [%]
def efficiency(n):
    return panel_file['Efficiëntie bij 25°'][n]

# Get temperature power factor of a solar panel [/°C]
def tempfac(n):
    return panel_file['Procentuele daling efficiëntie per graad celcius'][n]/100

# Get lifetime of a solar panel [yr]
def lifetime(n):
    return panel_file['Garantie levensduur'][n]

# Get yearly power degradation of a solar panel [/yr]
def degradation(n):
    return panel_file['Procentuele daling vermogen per jaar'][n]/100

# Get linear degradation lifetime [yr]
def linear_lifetime(n):
    return panel_file['Garantie lineaire power degradatie'][n]

# Get dimensions of a solar panel [mm^2]
def dimensions(n):
    return panel_file['Dimensies'][n]

# Get price of a solar panel [€]
def price(n):
    return panel_file['Prijs'][n]

# Get area of solar panel [m^2]
def area(n):
    dims = dimensions(n)
    return int(dims[0:4])*int(dims[5:9])/10**6

'''Function to calculate the panel gains in kWh every quarter. This information will later be used to calculate the profit of our investment.
A help function to calculate the actual efficiency in every quarter is needed.'''
# Get data frame of actual efficiency of solar panel [%]
# The given efficiency must be corrected with the temperature of the panel and the yearly power degradation
# Reference temperature for given efficiency (STC)
T_stc = 25  
def acteff(n, year, flat=True):
    if flat:
        panel_temp = solar_data_file['T_flat']
    else:
        panel_temp = solar_data_file['T_gable']
    return efficiency(n) * (1 + (year-2023)*degradation(n)) * (1 + (panel_temp-T_stc)*tempfac(n))

# Corrigated solar irradiance is needed to calculate the panel gains in every quarter [W/m^2]
solar_irradiance = solar_data_file[['DayNumber', 'GlobRad', 'DiffRad']].apply(sa.poa_irradiance, axis=1, args=(tilt_angle, orientation_angle, latitude, longitude, 1))

# Get energy gain of panels [kWh]
def panel_gains(n, inv, number_of_panels, year, flat=True):
    actual_efficiency = acteff(n, year, flat)
    # The maximum energy that the invertor can let through in a quarter (/4000 to go from Watt-quarter to kWh) [kWh]
    max_energy_invertor = invertor_data_file['DC POWER'][inv]/4000
    efficiency_invertor = invertor_data_file['EFF'][inv]
    # The solar panel gains (/4000 to go from Watt-quarter to kWh) [kWh]
    untouched_gains = actual_efficiency/100*solar_irradiance*number_of_panels*area(n)/4000
    # The gains corrigated with the maximum energy of the invertor [kWh]
    maximum_gains_inv = untouched_gains.apply(lambda x: min(x,max_energy_invertor))
    return (1 - cable_losses)*(1-dust_losses)*maximum_gains_inv*efficiency_invertor/100

'''Price functions'''
# Adapt the price of electricity or other goods with an estimated inflation rate [€]
def price_in_year(start_price, year):
    return start_price * (1 + inflation_rate)**(year-2023)

# Prosument_tarif cost for certain invertor in certain year [€]
def prosument_tarif(year, inv):
    # /1000 to go from Watt to kilowatt
    return prosument_tarif_inv*invertor_data_file['DC POWER'][inv]/1000*(1 + inflation_rate)**(year-2023)

# Price invertor in certain year [€]
def p_invertor(year, inv):
    return invertor_data_file['PRICE'][inv]*(1+inflation_rate)**(year-2023)

'''Gain functions: comparison between with and without panels. Output values are what we have to pay less for electricity in case of solar panels'''
# Capcity gain: the difference in what we have to pay for the capacity tarif when we have solar panels [€]
def capacity_gain_per_year(n, inv, number_of_panels, year, flat = True):
    # The load list per month will contain 12 load profile dataframe columns as elements of the 12 months [kW]
    load_list_per_month = list()
    # The difference list per month will contain the difference between load and production 
    difference_list_per_month = list()
    # Get the energy of the panels in each quarter
    solar_gains = panel_gains(n, inv, number_of_panels, year, flat)
    # Loop over the months
    month = 1
    while month < 13:
        # Number of quarters in the month
        if month in {1,3,5,7,8,10,12}:
            number_of_quarters = 96*31
        elif month == 2:
            number_of_quarters = 96*28
        else:
            number_of_quarters = 96*30
        # Select month from dataframe, go from kWh to kW by *4
        month_load = load_profile['Load_kW'][str(month)+'/1/2018 00:00:00':str(month)+'/'+str(int(number_of_quarters/96))+'/2018 23:45:00']
        month_gain = solar_gains[str(month)+'/1/2018 00:00:00':str(month)+'/'+str(int(number_of_quarters/96))+'/2018 23:45:00']*4
        # Add month to list
        load_list_per_month.append(month_load)
        difference_list_per_month.append(month_load - month_gain)
        month += 1
    # Calculate sum of maximal values (load for case without panels, difference for case with panels)
    sum_of_maximal_load = 0
    sum_of_maximal_difference = 0
    for m in range(len(load_list_per_month)):
        sum_of_maximal_load += max(load_list_per_month[m])
        sum_of_maximal_difference += max(difference_list_per_month[m])
    # You pay at least for a mean of 2.5 kW
    return capacity_tarif*(max(sum_of_maximal_load/12, 2.5)-max(sum_of_maximal_difference/12, 2.5))

# Help function for the extra taxes. Calculates the energy taken from the grid in a year [kWh]
def energy_from_grid_per_year(n, inv, number_of_panels, year, flat=True, digital=True):
    # Calculate netto consumption in each quarter
    comparison = load_profile['Load_kW']/4 - panel_gains(n, inv, number_of_panels, year, flat)
    # Set negative values to zero
    energy_from_grid_per_quarter = comparison.apply(lambda x: max(x,0))
    return sum(energy_from_grid_per_quarter)

# Heffingen  gain: the difference in what we have to pay for extra taxes when we have solar panels [€]
# In case of digital, we have to look in every quarter if we are taking from the net. In case of analog, we need to look at the netto consumption
def heffingen_gain_per_year(n, inv, number_of_panels, year, flat=True, digital=True):
    if digital:
        return (sum(load_profile['Load_kW']/4) - energy_from_grid_per_year(n, inv, number_of_panels, year, flat, digital))*price_in_year(heffingen_start, year)
    else:
        # Calculate netto consumption in each quarter
        comparison = load_profile['Load_kW']/4 - panel_gains(n, inv, number_of_panels, year, flat)
        return (sum(load_profile['Load_kW']/4) - max(sum(comparison),0))*price_in_year(heffingen_start, year)

# Total profit in a year
# Calculate what we win for our electricity during one year by having solar panels. For a digital meter, we need to compare the load and the production in every
# quarter to make sure we get the right price for putting energy back on the grid and for taking energy of the grid. What we win in a quarter is the price we have 
# to pay for our load without solar panels minus the price we have to pay when our load is greater than our production or plus the money we get when our production is
# greater than our load. However, for a classic meter, we get nothing for the net overproduction we have at the end of a year. Since the price to get electricity from
# the net is the same as the price to put electricity on the grid (since the meter just turns backwards) as long as we don't have overproduction, it is easier to perform
# this calculation on yearly basis.
def profit_panels_per_year(n, inv, number_of_panels, year, flat=True, digital=True):
    # Calculate netto consumption in each quarter [kWh]
    comparison = load_profile['Load_kW']/4 - panel_gains(n, inv, number_of_panels, year, flat)
    if digital:
        profit_in_quarters = price_in_year(p_op_start, year)*comparison.apply(lambda x: -min(x,0)) - price_in_year(p_van_start_digital, year)*comparison.apply(lambda x: max(x,0)) + price_in_year(p_van_start_digital, year)*load_profile['Load_kW']/4
        panel_profit = sum(profit_in_quarters) + capacity_gain_per_year(n, inv, number_of_panels, year, flat) + heffingen_gain_per_year(n, inv, number_of_panels, year, flat, digital)
    else:
        # Set to zero if we have netto production
        panel_profit = -max(sum(comparison), 0)*price_in_year(p_van_start_classic, year) + price_in_year(p_van_start_classic, year)*sum(load_profile['Load_kW']/4) + heffingen_gain_per_year(n, inv, number_of_panels, year, flat, digital)
    return panel_profit

'''Investment results'''
invertor_lifetime = 12
# Calculate profit of investment at the beginning of year_to_be_studied with a certain discount over the years
def profit_of_investment(n, inv, number_of_panels, year_to_be_studied, discount, flat=True, digital=True):
    # Start at minus investment cost
    profit = (-number_of_panels*price(n)-p_invertor(2023, inv))*(1+installation)
    for year in range(year_to_be_studied-2023):
        # Replace invertor if needed
        if year == invertor_lifetime:
            # Niet zeker of er hier gedeeld moet worden door de discount
            profit += -p_invertor(2023 + year,inv)/((1+discount)**year)
        # Add profit of every year
        profit += profit_panels_per_year(n, inv, number_of_panels, year + 2023, flat, digital)/((1+discount)**year)
    return profit

# for n in range(25):
#     print(profit_of_investment(10,5,10,n+2023,0.08), n+2023)

# for n in range(25):
#     print(profit_of_investment(10,5,10,n+2023,0.05, flat=True, digital=False))


# Calculate profit of investment at end date
def eventual_profit_of_investment(n, inv, number_of_panels, waranty_weight, discount, flat=True, digital=True):
    year_to_be_studied = 30 + waranty_weight*(lifetime(n)-25)
    return profit_of_investment(n, inv, number_of_panels, year_to_be_studied + 2023, discount, flat, digital)

# print(eventual_profit_of_investment(10, 5, 10, 0, 0.05, flat=True, digital=True))
# print(eventual_profit_of_investment(10, 5, 10, 0, 0.05, flat=True, digital=False))

# Calculate payback time of investment
def payback_time(n, inv, number_of_panels, discount, flat=True, digital=True):
    year_to_be_studied = 2023
    while year_to_be_studied < 2123:
        if profit_of_investment(n, inv, number_of_panels, year_to_be_studied, discount, flat, digital) > 0:
            return year_to_be_studied
        else:
            year_to_be_studied += 1
    return print('No payback time reached in a 100 years')

#print(payback_time(10,5,10,0.05))


#Optimal setup

for tilt_angle_for in {10,15,20,25,30,35,40,45}:
    for orientation_angle_for in {0,90,180,270}: 
        for panel in {1,3,10,21,28}:
            for inverter in range(1,len(invertor_data_file)):
                for amount_of_panels in {1:24}:
                    solar_irradiance = solar_data_file[['DayNumber', 'GlobRad', 'DiffRad']].apply(sa.poa_irradiance, axis=1, args=(tilt_angle_for, orientation_angle_for, latitude, longitude, 1))
                    invertor_data_file['EFF'][inverter]
                    print('performance:', profit_of_investment(panel,inverter,amount_of_panels,2048,0.05,True,True), panel, inverter, amount_of_panels,tilt_angle_for,orientation_angle_for)

