from matplotlib import pyplot
from main import df_irr

''' irradiance and temperature data plot '''

# pyplot.plot(df_irr.index, df_irr['GlobRad'])
# pyplot.title("Global Radiation")
# pyplot.show()
#
# pyplot.plot(df_irr.index, df_irr['DiffRad'])
# pyplot.title("Diffusion Radiation")
# pyplot.show()
#
# pyplot.plot(df_irr.index, df_irr['T_gable'])
# pyplot.title("Temperature of gable rood")
# pyplot.show()
#
# pyplot.plot(df_irr.index, df_irr['T_flat'])
# pyplot.title("Temperature of flat roof")
# pyplot.show()


''' solar angle plots '''

# pyplot.plot(df_irr.index, df_irr['DeclinationAngle'])
# pyplot.title("Declination Angle")
# pyplot.show()
#
# pyplot.plot(df_irr.index, df_irr['SolarTimeDifference'])
# pyplot.title("Difference between solar time and local time")
# pyplot.show()
#
# pyplot.plot(df_irr.index, df_irr['HourAngle'])
# pyplot.title("Hour Angle")
# pyplot.show()
#
# pyplot.plot(df_irr.index, df_irr['ElevationAngle'])
# pyplot.title("Elevation Angle")
# pyplot.show()
#
# pyplot.plot(df_irr.index, df_irr['AzimuthAngle'])
# pyplot.title("Azimuth Angle")
# pyplot.show()
#
# pyplot.plot(df_irr.index, df_irr['IncidenceAngle'])
# pyplot.title("Incidence Angle")
# pyplot.show()
#
# pyplot.plot(df_irr.index, df_irr['EffComplementaryIncidenceAngle'])
# pyplot.title("Effective Complementary Incidence Angle")
# pyplot.show()

''' plane of array irradiance plots '''

# fig, ax = pyplot.subplots()
# ax.plot(df_irr.index, df_irr['POABeam'], label='Beam')
# ax.plot(df_irr.index, df_irr['POAGroundEffect'], label='Ground Effect')
# ax.plot(df_irr.index, df_irr['POASkyDiffusion'], label='Sky Diffusion')
# ax.legend(loc='upper right')
# ax.set_xlabel('Date and Time')
# ax.set_ylabel('POA Irradiance [$\\frac{W}{m^2}$]')
# pyplot.title("POA all 3 components")
# pyplot.show()
#
# fig, ax = pyplot.subplots()
# ax.plot(df_irr.index, df_irr['POAIrradiance'])
# ax.set_xlabel('Date and Time')
# ax.set_ylabel('POA Irradiance [$\\frac{W}{m^2}$]')
# ax.set_title('Plane of Array Irradiance')
# pyplot.show()
#
# fig, ax = pyplot.subplots()
# ax.plot(df_irr.index, df_irr['POAIrradiance_0'], label='$\\beta = 0°$')
# ax.plot(df_irr.index, df_irr['POAIrradiance_10'], label='$\\beta = 10°$')
# ax.plot(df_irr.index, df_irr['POAIrradiance_20'], label='$\\beta = 20°$')
# ax.plot(df_irr.index, df_irr['POAIrradiance_30'], label='$\\beta = 30°$')
# ax.plot(df_irr.index, df_irr['POAIrradiance_40'], label='$\\beta = 40°$')
# ax.legend(loc='upper right')
# ax.set_xlabel('Date and Time')
# ax.set_ylabel('POA Irradiance [$\\frac{W}{m^2}$]')
# pyplot.title("POA for different tilt angles")
# pyplot.show()

fig, ax = pyplot.subplots()
ax.plot(df_irr.index, df_irr['POAIrradiance180'], label='Northern orientation $\\theta_{pv} = 180°$' )
ax.plot(df_irr.index, df_irr['POAIrradiance270'], label='Eastern orientation $\\theta_{pv} = 270°$')
ax.plot(df_irr.index, df_irr['POAIrradiance0'], label='Southern orientation $\\theta_{pv} = 0°$')
ax.plot(df_irr.index, df_irr['POAIrradiance90'], label='Western orientation $\\theta_{pv} = 90°$')
ax.legend(loc='upper right')
ax.set_xlabel('Date and Time')
ax.set_ylabel('POA Irradiance [$\\frac{W}{m^2}$]')
pyplot.title("POA for different orientation angles")
pyplot.show()


fig, ax = pyplot.subplots()
ax.plot(df_irr.index, df_irr['POAIrradiance0'], label='South orientation')
ax.plot(df_irr.index, df_irr['POAIrradiance90270'], label='East-West orientation')
ax.legend(loc='upper right')
ax.set_xlabel('Date and Time')
ax.set_ylabel('POA Irradiance [$\\frac{W}{m^2}$]')
pyplot.title("POA for east-west orientation")
pyplot.show()
