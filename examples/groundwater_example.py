#!/usr/bin/env python3

# import data fetcher
from skdaccess.geo.groundwater import DataFetcher as WDF
from skdaccess.framework.param_class import *


# First, create a data fetcher of all stations
# and access data wrapper and meta data
fullDF = WDF()
fullDW = fullDF.output()
meta_data = WDF.getStationMetadata()


# Get an iterator to the data
dataIT = fullDW.getIterator()


# The iterator access returns the data label, the data, and uncertainties.
# In the case of groundwater data, no uncertainties are given
label_1, data_1, error = next(dataIT)
label_2, data_2, error = next(dataIT)



# Try to plot the first two groundwater stations:
try:
    import matplotlib.pyplot as plt
    plt.gcf().set_size_inches(14,4)
    plt.ylabel(label_1)
    plt.title(data_1.name)
    plt.plot(data_1);
    plt.figure().set_size_inches(14,4)
    plt.ylabel(label_2)
    plt.title(data_2.name)
    plt.plot(data_2,color='red')

    plt.show()

except ImportError as e:
    pass

