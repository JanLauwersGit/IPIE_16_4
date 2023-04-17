from data_processing import *
import pandas as pd
import datetime as dt


''' parameters '''

start_datetime = dt.datetime(2018, 1, 1, 0, 0, 0)
end_datetime = dt.datetime(2018, 12, 31, 23, 59, 59)
timedelta_irr = dt.timedelta(minutes=1)  # timedelta used for filling the missing dates in the raw data
timedelta_load = dt.timedelta(minutes=15)
irr_seasonal_data_columns = ['GlobRad', 'DiffRad', 'T_gable', 'T_flat']
load_seasonal_data_columns = ['Load']
number_proxy_days_for_average = 7  # this cant be too big, because there will be an asymmetry if dates before are available, but dates after not...
time_interval = dt.timedelta(minutes=15)


""" IRRADIANCE DATA """
''' importing data from csv file and formatting '''

df_irr = pd.read_csv(r'/Users/moiravandenberghe/Documents/semester2/IPIE/IrradianceDataRaw.csv', sep=';')
df_irr = df_irr.replace(',', '.', regex=True)
df_irr.DateTime = pd.to_datetime(df_irr.DateTime, format='%d/%m/%Y %H:%M')
df_irr = df_irr.astype({'GlobRad': 'float', 'DiffRad': 'float', 'T_gable': 'float', 'T_flat': 'float'})


''' filling missing dates '''

df_irr = fill_missing_dates(df_irr, start_datetime, end_datetime, timedelta_irr)
day_number_values = df_irr.DateTime.apply(day_from_date)
df_irr.insert(1, 'DayNumber', day_number_values)
df_irr = df_irr.set_index('DateTime')


''' filling missing data '''

df_irr = data_imputation(df_irr, irr_seasonal_data_columns, number_proxy_days_for_average, timedelta_irr)
df_irr['GlobRad'] = df_irr[['GlobRad', 'DiffRad']].apply(compare_globrad_diffrad, axis=1)


''' save dataframe as csv file '''
df_irr.reset_index(drop=False, inplace=True)
df_irr.to_csv(r'/Users/moiravandenberghe/Documents/semester2/IPIE/IrradianceData.csv', index=False, sep=';')
# df_irr.to_excel(r'/Users/moiravandenberghe/Documents/semester2/IPIE/IrradianceData.xlsx', index=False)


# """ LOAD PROFILE """
# ''' importing data from csv file and formatting '''
#
# df_load = pd.read_csv(r'/Users/moiravandenberghe/Documents/semester2/IPIE/LoadProfileRaw.csv', sep=';')
# df_load = df_load.replace(',', '.', regex=True)
# df_load.DateTime = pd.to_datetime(df_load.DateTime, format='%d/%m/%Y %H:%M:%S')
# df_load = df_load.astype({'Load': 'float'})
#
#
# ''' filling missing dates '''
#
# df_load = fill_missing_dates(df_load, start_datetime, end_datetime, timedelta_load)
# day_number_values = df_load.DateTime.apply(day_from_date)
# df_load.insert(1, 'DayNumber', day_number_values)
# df_load = df_load.set_index('DateTime')
#
#
# ''' filling missing data '''
#
# df_load = data_imputation(df_load, load_seasonal_data_columns, number_proxy_days_for_average, timedelta_load)
# pyplot.plot(df_load.index, df_load.Load)
# pyplot.show()
#
#
# ''' save dataframe as csv file '''
#
# df_load.reset_index(drop=False, inplace=True)
# df_load.to_csv(r'/Users/moiravandenberghe/Documents/semester2/IPIE/LoadProfile.csv', index=False)
