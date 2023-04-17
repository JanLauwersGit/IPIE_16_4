import numpy as np
import math

# All angles are given in degrees and only locally converted to radians for calculations
# Day parameter is a continuous count of days and fractions elapsed since 1 jan 2018


def declination_angle(day):
    """
    :param day as a decimal corresponding to the day and time of the year
    :return: declination angle in degrees
    """

    declination_rad = -np.deg2rad(23.45) * np.cos(2*np.pi/365*(day+10))
    declination = np.rad2deg(declination_rad)

    return declination


def local_solar_time(day, longitude, time_zone):
    """
    :param day: day as a decimal corresponding to the day and time of the year
    :param longitude: longitude
    :param time_zone: time zone with respect to UTC
    :return: local solar time in format of a decimal number corresponding with the day of the year
    """

    lstm = 15*time_zone # local standard time meridian
    b = np.deg2rad(360/365 * (day-81))
    eot = 9.87 * np.sin(2*b) - 7.53 * np.cos(b) - 1.5 * np.sin(b)  # equation of time
    tc_minutes = 4 * (longitude - lstm) + eot  # time correction
    tc_days = tc_minutes / (60 * 24)
    lst = day + tc_days

    return lst


def solar_time_difference(day, longitude, time_zone):
    """
    :param day: day as a decimal corresponding to the day and time of the year
    :param longitude: longitude
    :param time_zone: time zone with respect to UTC
    :return: difference between local time and local solar time in minutes, positive when local time is ahead of local solar time.
    """
    lst = local_solar_time(day, longitude, time_zone)
    std = day - lst
    std = std * 24 * 60

    return std


def hour_angle(day, longitude, time_zone):

    lst = local_solar_time(day, longitude, time_zone)
    lst_in_hours = 24 * math.fmod(lst, 1.0)
    hra = 15 * (lst_in_hours - 12)

    return hra


def elevation_angle(day, longitude, time_zone):
    """
    :param day: day as a decimal corresponding to the day and time of the year
    :param longitude: longitude
    :param time_zone: time zone with respect to UTC
    :return: elevation angle in degrees
    """

    declination = declination_angle(day)
    declination_rad = np.deg2rad(declination)

    longitude_rad = np.deg2rad(longitude)

    hra = hour_angle(day, longitude, time_zone)
    hra_rad = np.deg2rad(hra)

    elevation_rad = np.arcsin(np.sin(declination_rad) * np.sin(longitude_rad) + np.cos(declination_rad) * np.cos(longitude_rad) * np.cos(hra_rad))
    elevation = np.rad2deg(elevation_rad)

    return elevation


def azimuth_angle(day, latitude, longitude, time_zone):
    """
    :param day:
    :param latitude:
    :param longitude:
    :param time_zone:
    :return:
    """
    latitude_rad = np.deg2rad(latitude)

    declination = declination_angle(day)
    declination_rad = np.deg2rad(declination)

    hra = hour_angle(day, longitude, time_zone)
    hra_rad = np.deg2rad(hra)

    azimuth_rad = np.arctan2(np.sin(hra_rad), np.cos(hra_rad) * np.sin(latitude_rad) - np.tan(declination_rad) * np.cos(latitude_rad))
    azimuth = np.rad2deg(azimuth_rad)

    return azimuth


def incidence_angle(day, tilt_angle, orientation_angle, latitude, longitude, time_zone):  # angle between the incoming sunlight and the normal to the surface of the PV panel
    """
    :param day:
    :param tilt_angle:
    :param orientation_angle:
    :param latitude:
    :param longitude:
    :param time_zone:
    :return:
    """
    elevation = elevation_angle(day, longitude, time_zone)
    zenith_rad = np.deg2rad(90-elevation)

    azimuth = azimuth_angle(day, latitude, longitude, time_zone)
    azimuth_rad = np.deg2rad(azimuth)

    tilt_rad = np.deg2rad(tilt_angle)

    orientation_rad = np.deg2rad(orientation_angle)

    cos_theta = np.cos(zenith_rad) * np.cos(tilt_rad) + np.sin(zenith_rad) * np.sin(tilt_rad) * np.cos(azimuth_rad - orientation_rad)
    theta = np.arccos(cos_theta)
    incidence = np.rad2deg(theta)

    return incidence


def eff_complementary_incidence_angle(day, tilt_angle, orientation_angle, latitude, longitude, time_zone):  # just use for plot visualization
    """
    :param day:
    :param tilt_angle:
    :param orientation_angle:
    :param latitude:
    :param longitude:
    :param time_zone:
    :return:
    """
    incidence = incidence_angle(day, tilt_angle, orientation_angle, latitude, longitude, time_zone)

    if incidence > 90:
        incidence = 90

    eff_complementary_incidence = 90 - incidence

    return eff_complementary_incidence


def direct_normal_irradiance(df, longitude, time_zone):

    elevation = elevation_angle(df['DayNumber'], longitude, time_zone)
    if elevation < 0:
        elevation = 0
    zenith_rad = np.deg2rad(90 - elevation)

    dni = (df['GlobRad'] - df['DiffRad']) / max(np.cos(zenith_rad), 0.1)

    return dni


def poa_beam(df, tilt_angle, orientation_angle, latitude, longitude, time_zone):

    dni = direct_normal_irradiance(df, longitude, time_zone)

    incidence = incidence_angle(df['DayNumber'], tilt_angle, orientation_angle, latitude, longitude, time_zone)
    if incidence > 90:
        incidence = 90
    incidence_rad = np.deg2rad(incidence)

    poa_beam = dni * np.cos(incidence_rad)

    return poa_beam


def poa_ground_effect(global_irr, tilt_angle, albedo=0.18):

    poa_ground_effect = global_irr * albedo * (1-np.cos(tilt_angle))/2

    return poa_ground_effect


def poa_sky_diffusion(diffusion_irr, tilt_angle):

    poa_sky_diffusion = diffusion_irr * (1 + np.cos(tilt_angle))/2

    return poa_sky_diffusion


def poa_irradiance(df, tilt_angle, orientation_angle, latitude, longitude, time_zone, albedo=0.18):

    beam = poa_beam(df, tilt_angle, orientation_angle, latitude, longitude, time_zone)
    ground_effect = poa_ground_effect(df['GlobRad'], tilt_angle, albedo)
    sky_diffusion = poa_sky_diffusion(df['DiffRad'], tilt_angle)

    poa_irradiance = beam + ground_effect + sky_diffusion

    return poa_irradiance
