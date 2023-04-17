import datetime as dt
import pandas as pd
import numpy as np
from scipy.optimize import curve_fit
from matplotlib import pyplot


def change_time_interval(df, time_interval):

    df_resampled = df.resample(time_interval).mean()

    return df_resampled


def day_from_date(local_time):
    """
    :param local_time: date and time in format 'yyyy-mm-dd hh:mm:ss'
    :return: number of the day of the year, in decimal form according to the time of day
    """
    year = local_time.year
    start_time = dt.datetime(year, 1, 1, 0, 0, 0)
    timedelta = local_time - start_time
    total_seconds = timedelta.total_seconds()
    day = total_seconds / (24 * 60 * 60) + 1

    return day


def compare_globrad_diffrad(df):
    if df['GlobRad'] < df['DiffRad']:
        df['GlobRad'] = df['DiffRad']
    return df


def date_from_day(day, year):
    """
    :param day as a decimal corresponding to the day and time of the year
    :return: date and time in the format 'yyyy-mm-dd hh:mm:ss'
    """
    start_date = dt.datetime(year, 1, 1, 0, 0, 0)
    date = start_date + dt.timedelta(days=day-1)
    return date


def fill_missing_dates(df, start_datetime, end_datetime, timedelta):
    """
    :param df: dataframe with 'DateTime' column as first column and n other columns
    :param start_datetime:
    :param end_datetime:
    :param timedelta:
    :return:
    """

    all_dates = pd.date_range(start_datetime, end_datetime, freq=timedelta)
    missing_dates = all_dates[~all_dates.isin(df.DateTime)]

    missing_data = {'DateTime': missing_dates}
    for col in df.columns[1:]:
        missing_data[col] = [None] * len(missing_dates)

    missing_df = pd.DataFrame(missing_data)

    filled_df = pd.concat([df, missing_df], sort=False)
    filled_df = filled_df.sort_values('DateTime').reset_index(drop=True)

    return filled_df


def find_missing_periods(df_col, timedelta):  # works on one column

    df_col = df_col.dropna()
    time_diffs = pd.Series(df_col.index).diff()
    time_diffs = time_diffs.fillna(timedelta)
    missing_indices = pd.Series(time_diffs != timedelta)

    missing_periods = pd.DataFrame(columns=['StartTime', 'EndTime'])

    for i, is_missing in enumerate(missing_indices):
        if is_missing:
            start_time = df_col.index[i-1]
            end_time = (df_col.index[i] - timedelta)

            missing_periods = missing_periods.append({'StartTime': start_time, 'EndTime': end_time}, ignore_index=True)

    return missing_periods


def seasonal_trend(df):
    """
    :param df: only the columns with seasonal data
    :return:
    """

    daily_mean = df.groupby(df.index.dayofyear).mean()
    daily_mean = daily_mean.dropna()

    df_seasonal_trend = pd.DataFrame(index=daily_mean.index)

    def func(x, a, b, c, d):  # define the modified sine function to fit to the data
        return a * np.sin(b * x + c) + d

    x = np.array(daily_mean.index)  # numpy array of the day of the year values
    y = np.array(daily_mean.values)  # numpy array of the daily mean values

    amplitude = daily_mean.max()
    frequency = 2 * np.pi / 365
    p0 = [amplitude, frequency, 0, 1]  # initial guesses for the parameters

    popt, pcov = curve_fit(func, x, y, p0=p0)  # fit the curve to the daily mean data
    curve = func(x, *popt)  # predict the curve values for each day of the year
    df_seasonal_trend['CurveValues'] = curve  # create a new column in the curve dataframe with the curve values corresponding to the index

    # pyplot.plot(daily_mean.index, daily_mean[col])
    # pyplot.plot(df_curve.index, df_curve[col])
    # pyplot.show()

    df_seasonal_trend = df_seasonal_trend.reindex(range(1, 366)).interpolate()

    return df_seasonal_trend


def average_profile_proximate_days(df, missing_period, number_of_days):

    start_day = missing_period.iloc[0, 0].dayofyear  # last day before data gap with data for entire day
    end_day = missing_period.iloc[0, 1].dayofyear  # first day after data gap with data for entire day
    proximate_days_list = []
    for i in range(number_of_days):
        if 0 <= start_day - i <= 365:
            proximate_days_list.append(start_day-1-i)
            proximate_days_list.append(end_day+1+i)

    df_proximate_days = df[df.index.dayofyear.isin(proximate_days_list)]
    df_proximate_days = df_proximate_days.dropna()

    average_profile = df_proximate_days.groupby(df_proximate_days.index.time).mean()
    average_profile = average_profile.sort_index()
    #average_profile.index = pd.to_datetime(average_profile.index, format='%H:%M:%S') uncomment this if you want to plot the results

    return average_profile


def data_imputation(df,  seasonal_data_columns, number_of_days, timedelta):
    missing_periods = find_missing_periods(df, timedelta)
    for col in df[seasonal_data_columns]:
        pyplot.plot(df.index, df[col])
        pyplot.show()
        for i in missing_periods.index:
            df_seasonal_trend = seasonal_trend(df[col])
            df[col] = data_imputation_one_column_one_period(df[[col]], df_seasonal_trend, missing_periods.iloc[[i]], number_of_days)
            pyplot.plot(df.index, df[col])
            pyplot.show()

    return df


def data_imputation_one_column_one_period(df, df_seasonal_trend, missing_period, number_of_days):

    average_profile = average_profile_proximate_days(df, missing_period, number_of_days)
    start_day = missing_period.iloc[0, 0].dayofyear
    end_day = missing_period.iloc[0, 1].dayofyear
    date = missing_period.iloc[0, 0]
    timedelta = dt.timedelta(days=1)

    for day in range(start_day, end_day+1):

        seasonal_average = df_seasonal_trend.loc[day, 'CurveValues']
        current_average = average_profile.mean()
        scaling_factor = seasonal_average / current_average
        df_fill = average_profile * scaling_factor

        fixed_date = dt.datetime(date.year, date.month, date.day)
        datetime_index = [dt.datetime.combine(fixed_date, t) for t in df_fill.index]
        df_fill.index = pd.to_datetime(datetime_index)

        df = df.combine_first(df_fill)
        date = date + timedelta

    df_filled = df

    return df_filled








