import datetime as dt
import matplotlib as mpl
import numpy as np
from matplotlib import pyplot

# visual studio code
# spyder

from main import df_irr

pyplot.plot(df_irr.index, df_irr.GlobRad)
pyplot.show()

resampled = df_irr.resample('H').interpolate()

pyplot.plot(df_irr.index, df_irr.GlobRad)
pyplot.show()

print(resampled)


time_test = dt.datetime(2018, 3, 13, 15, 38, 00)
print(df_irr.loc[time_test]['GlobRad'])


# datetime formatting and index
#date = df_irr["DateTime"].dt.date
#time = df_irr["DateTime"].dt.time
#df_irr.insert(1, "Date", date)
#df_irr.insert(2, "Time", time)
#df_irr = df_irr.set_index('DateTime')

#pd.set_option('display.max_columns', None)
#pd.set_option('display.max_columns', None)
#print(df_irr)


# declination and elevation angle calculation
#N = 10
#t1 = time.time()
#for i in range(0, N):
#    df_irr['DeclinationAngle'] = df_irr['DateTime'].apply(declination_angle)
#t2 = time.time()
#print((t2-t1)/N)


class Person:

    def __init__(self, d):
        self.name = d["name"]
        self.age = d["age"]
        self.gender = d["gender"]

    def __str__(self):
        return "person :" + str(self.name)
