# The MIT License (MIT)
# Copyright (c) 2016 Massachusetts Institute of Technology
#
# Author: Justin D Li
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


'''@package trend_util
This module is designed to provide a suite of tools for quick analysis of
the linear and sinusoidal (annual, semi-annual, seasonal, and monthly)
trends of time-series data (formatted using the pandas format).
'''


import numpy as np
import pandas as pd
from scipy import optimize
from scipy.ndimage import median_filter


## The getTrend function applies the signal.detrend function, but also tries to
#  return the trend, given a time index input.
#  Input:
#   - xdata, 1D time-series data in a pandas series format
#
#  Output:
#    - xdetr, the detrended data in pandas series format
#    - trend, the linear trend parameters assuming a 1 day per sample time fit
def getTrend(xdata):
    # returns detrended data and the trend
    # checks the time frequency to create a time vector
    if xdata.index.freq != pd.tseries.offsets.Day():
        print('Frequency of Sampling is not Day, please check that resampling occurred!')
    timeDat = np.arange(0,len(xdata.index))
    dataDat = xdata
    # remove time and data with NaN's for now
    ninds = np.array(pd.isnull(dataDat)==True)
    argtd = (timeDat[ninds==False],dataDat[ninds==False])
    
    fitfunc = lambda p, x: p[0]*x+p[1]          # Target function (linear)
    errfunc = lambda p, x, y: fitfunc(p, x) - y # Distance to the target function
    pAnnual = [1., 5.]                          # Initial guess for the parameters
    pA, success = optimize.leastsq(errfunc, pAnnual[:], args=argtd)
    trend = fitfunc(pA, timeDat)

    # puts the data back into the pandas series format to recover the time index
    xdetr = pd.core.series.Series(data=dataDat-trend,index=xdata.index)
    
    return xdetr, trend



## The sinuFits function tries to fit annual and semi-annual sinusoid trends to
#  the data. Other options allow for a monthly and seasonal sinusoid fit. The
#  data is expected to be a pandas format data
#  Input:
#   - xdata, 1D time-series data in a pandas series format
#   - fitN, the number of sinusoids to fit. annual, semi-annual, seasonal, monthly
#   - rmve, a flag to return sinusoid removed data, or the sinusoids
#
#  Output:
#    - retrDat, the returned data, either sinusoid removed or the sum of the sinusoids
def sinuFits(xdata,fitN=2,rmve=1):
    # checks the time frequency to create a time vector
    if xdata.index.freq != pd.tseries.offsets.Day():
        print('Frequency of Sampling is not Day, please check that resampling occurred!')
    timeDat = np.arange(0,len(xdata.index))
    # ignores time and data with NaN's for now
    ninds = np.array(pd.isnull(xdata)==True)
    argtd = (timeDat[ninds==False],xdata[ninds==False])
    if fitN >= 1:
        # annual (365 day period) sinusoidal fit
        fitfunc = lambda p, x: p[0]*np.cos(2*np.pi/365*x+p[1]) + p[2]
        errfunc = lambda p, x, y: fitfunc(p, x) - y
        pAnnual = [5., 0., 0.]
        pA, success = optimize.leastsq(errfunc, pAnnual[:], args=argtd)
        retrDat = fitfunc(pA, timeDat)
    if fitN >= 2:
        # semi-annual (182.5 day period) sinusoidal fit
        fitfunc = lambda p, x: p[0]*np.cos(2*np.pi/182.5*x+p[1]) + p[2]
        errfunc = lambda p, x, y: fitfunc(p, x) - y
        pAnnual = [5., 0., 0.]
        pSA, success = optimize.leastsq(errfunc, pAnnual[:], args=argtd)
        retrDat += (fitfunc(pSA, timeDat))
    if fitN >= 3:
        # seasonal / quarterly (91.25 day period) sinusoidal fit
        fitfunc = lambda p, x: p[0]*np.cos(2*np.pi/91.25*x+p[1]) + p[2]
        errfunc = lambda p, x, y: fitfunc(p, x) - y
        pAnnual = [5., 0., 0.]
        pSS, success = optimize.leastsq(errfunc, pAnnual[:], args=argtd)
        retrDat += (fitfunc(pSS, timeDat))
    if fitN >= 4:
        # monthly (30.5 day period) sinusoidal fit
        fitfunc = lambda p, x: p[0]*np.cos(2*np.pi/30.5*x+p[1]) + p[2]
        errfunc = lambda p, x, y: fitfunc(p, x) - y
        pAnnual = [5., 0., 0.]
        pM, success = optimize.leastsq(errfunc, pAnnual[:], args=argtd)
        retrDat += (fitfunc(pM, timeDat))
        
    if rmve==1:
        # if remove flag (rmve) is true, returns the data with the trend removed
        # otherwise, it returns the estimated overall, all components summed, trend
        retrDat = xdata - retrDat
            
    return retrDat
    
    
    
## A simple wrapper for the linear interpolation function from Numpy to fill in NaN's.
#  Modified slightly from sample code at ref: http://stackoverflow.com/questions/6518811/interpolate-nan-values-in-a-numpy-array
#  Input:
#   - data, 1d numpy or pandas array with possible NaN's
#
#  Output:
#   - interpolated data modified in place with endpoint NaN's extrapolated from closest non-NaN value
def interpNaN(data):
    # finds indicies of NaN's in the data
    nans,x = pd.isnull(data), lambda z: z.nonzero()[0]
    # interpolates in place
    data[nans] = np.interp(x(nans), x(~nans), data[~nans])


def medianFilter(data, window, interpolate=True):
    '''
    A median filter.  If interpolate is True, data will be interpolated before smoothering.
    Otherwise, all available data within the window will be used
    
    @param data: Input data
    @param window: Size of filter window
    @param interpolate: Interpolate data before smoothing

    @return Smoothed data
    '''

    if interpolate == True:
        interpNaN(data)
        result = pd.Series(median_filter(data, size=window), index=data.index)

    else:
        result = data.copy()
        for index, value in data.iteritems():
            if not pd.isnull(value):
                result.loc[index] = np.nanmedian(data[np.logical_and(data.index >= index-window/2,
                                                                     data.index <= index+window/2)])

    return result
