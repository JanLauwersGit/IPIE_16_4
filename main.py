from solar_angles import *
from data_processing import *
import subprocess
import pandas as pd


''' Parameters '''
# all angles are given in degrees, only internally in functions, they are converted to radians for calculations
initial_data_loading = False
generate_plots = False
year = 2018
time_interval = dt.timedelta(minutes=15)  # time interval used to reduce the size of the data frame by resampling

longitude = 5.5
latitude = 51
time_zone = 1

tilt_angle = 20
orientation_angle = 0


''' loading processed irradiance data '''

if initial_data_loading:
    subprocess.run(['python', 'initial_data_loading.py'])
df_irr = pd.read_csv('IrradianceData.csv')
df_irr.DateTime = pd.to_datetime(df_irr.DateTime, format='%Y-%m-%d %H:%M')
df_irr = df_irr.astype({'GlobRad': 'float', 'DiffRad': 'float', 'T_gable': 'float', 'T_flat': 'float'})
df_irr = df_irr.set_index('DateTime')
df_irr = change_time_interval(df_irr, time_interval)


''' solar angles calculations '''

df_irr['DeclinationAngle'] = df_irr.DayNumber.apply(declination_angle)
df_irr['LocalSolarTime'] = df_irr.DayNumber.apply(local_solar_time, args=(longitude, time_zone))
df_irr['SolarTimeDifference'] = df_irr.DayNumber.apply(solar_time_difference, args=(longitude, time_zone))
df_irr['HourAngle'] = df_irr.DayNumber.apply(hour_angle, args=(longitude, time_zone))
df_irr['ElevationAngle'] = df_irr.DayNumber.apply(elevation_angle, args=(longitude, time_zone))
df_irr['AzimuthAngle'] = df_irr.DayNumber.apply(azimuth_angle, args=(latitude, longitude, time_zone))
df_irr['IncidenceAngle'] = df_irr.DayNumber.apply(incidence_angle, args=(tilt_angle, orientation_angle, latitude, longitude, time_zone))
df_irr['EffComplementaryIncidenceAngle'] = df_irr.DayNumber.apply(eff_complementary_incidence_angle, args=(tilt_angle, orientation_angle, latitude, longitude, time_zone))


''' plane of array irradiance calculation '''

df_irr['POAIrradiance'] = df_irr[['DayNumber', 'GlobRad', 'DiffRad']].apply(poa_irradiance, axis=1, args=(tilt_angle, orientation_angle, latitude, longitude, time_zone))
df_irr['POABeam'] = df_irr[['DayNumber', 'GlobRad', 'DiffRad']].apply(poa_beam, axis=1, args=(tilt_angle, orientation_angle, latitude, longitude, time_zone))
df_irr['POAGroundEffect'] = df_irr['GlobRad'].apply(poa_ground_effect, args=(tilt_angle, ))
df_irr['POASkyDiffusion'] = df_irr['DiffRad'].apply(poa_sky_diffusion, args=(tilt_angle, ))

df_irr['POAIrradiance_0'] = df_irr[['DayNumber', 'GlobRad', 'DiffRad']].apply(poa_irradiance, axis=1, args=(0, orientation_angle, latitude, longitude, time_zone))
df_irr['POAIrradiance_10'] = df_irr[['DayNumber', 'GlobRad', 'DiffRad']].apply(poa_irradiance, axis=1, args=(10, orientation_angle, latitude, longitude, time_zone))
df_irr['POAIrradiance_20'] = df_irr[['DayNumber', 'GlobRad', 'DiffRad']].apply(poa_irradiance, axis=1, args=(20, orientation_angle, latitude, longitude, time_zone))
df_irr['POAIrradiance_30'] = df_irr[['DayNumber', 'GlobRad', 'DiffRad']].apply(poa_irradiance, axis=1, args=(30, orientation_angle, latitude, longitude, time_zone))
df_irr['POAIrradiance_40'] = df_irr[['DayNumber', 'GlobRad', 'DiffRad']].apply(poa_irradiance, axis=1, args=(40, orientation_angle, latitude, longitude, time_zone))

df_irr['POAIrradiance0'] = df_irr[['DayNumber', 'GlobRad', 'DiffRad']].apply(poa_irradiance, axis=1, args=(tilt_angle, 0, latitude, longitude, time_zone))
df_irr['POAIrradiance90'] = df_irr[['DayNumber', 'GlobRad', 'DiffRad']].apply(poa_irradiance, axis=1, args=(tilt_angle, 90, latitude, longitude, time_zone))
df_irr['POAIrradiance180'] = df_irr[['DayNumber', 'GlobRad', 'DiffRad']].apply(poa_irradiance, axis=1, args=(tilt_angle, 180, latitude, longitude, time_zone))
df_irr['POAIrradiance270'] = df_irr[['DayNumber', 'GlobRad', 'DiffRad']].apply(poa_irradiance, axis=1, args=(tilt_angle, 270, latitude, longitude, time_zone))
df_irr['POAIrradiance90270'] = df_irr[['POAIrradiance90', 'POAIrradiance270']].mean(axis=1)


# print('mean poa irradiance 0° tilt angle:', df_irr['POAIrradiance_0'].sum()/(12*365), 'W/m^2')
# print('mean poa irradiance 10° tilt angle:', df_irr['POAIrradiance_10'].sum()/(12*365), 'W/m^2')
# print('mean poa irradiance 20° tilt angle:', df_irr['POAIrradiance_20'].sum()/(12*365), 'W/m^2')
# print('mean poa irradiance 30° tilt angle:', df_irr['POAIrradiance_30'].sum()/(12*365), 'W/m^2')
# print('mean poa irradiance 40° tilt angle:', df_irr['POAIrradiance_40'].sum()/(12*365), 'W/m^2')

# print('mean poa irradiance southern orientation:', df_irr['POAIrradiance0'].sum()/(12*365), 'W/m^2')
# print('mean poa irradiance east-west orientation:', df_irr['POAIrradiance90270'].sum()/(12*365), 'W/m^2')
# print('mean poa irradiance northern orientation:', df_irr['POAIrradiance180'].sum()/(12*365), 'W/m^2')


''' generate print and plots '''

if generate_plots:
    import plots

pd.set_option('display.max_columns', None)
print(df_irr)


''' export result to csv '''

