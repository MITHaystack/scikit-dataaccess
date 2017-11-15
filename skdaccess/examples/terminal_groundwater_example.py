#!/usr/bin/env python3

# The MIT License (MIT)
# Copyright (c) 2016,2017 Massachusetts Institute of Technology
#
# Author: Cody Rude
# This software has been created in projects supported by the US National
# Science Foundation and NASA (PI: Pankratius)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.


# import data fetcher and AutoParams
from skdaccess.geo.groundwater import DataFetcher as WDF
from skdaccess.framework.param_class import *

# Create a data fetcher of stations within
# 35 < Latitude < 38, and -119 < Longitude < -118
# in the time period 2007-01-01 to 2016-12-31
fullDF = WDF([AutoParam(35), AutoParam(38), AutoParam(-119), AutoParam(-118)],
             '2007-01-01','2016-12-31',cutoff=0.0)

# Access data wrapper
fullDW = fullDF.output()

# Access metadata
meta_data = WDF.getStationMetadata()


# Get an iterator to the data
dataIt = fullDW.getIterator()


# The iterator returns the data label and the data.
label_1, data_1 = next(dataIt)
label_2, data_2 = next(dataIt)



# Try to plot the first two groundwater stations:
try:
    import matplotlib.pyplot as plt

    plt.figure().set_size_inches(14,4)
    plt.ylabel('Median Depth to Water Level')
    plt.title(label_1)
    plt.plot(data_1['Median Depth to Water']);
    plt.figure().set_size_inches(14,4)
    plt.ylabel('Median Depth to Water Level')
    plt.title(label_2);
    plt.plot(data_2['Median Depth to Water'],color='red')

    plt.show()

except ImportError as e:
    pass

