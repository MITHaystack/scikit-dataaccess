#!/usr/bin/env python3

# The MIT License (MIT)
# Copyright (c) 2016 Massachusetts Institute of Technology
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

