# The MIT License (MIT)
# Copyright (c) 2016, 2017, 2018 Massachusetts Institute of Technology
#
# Authors: Cody Rude
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


# Standard library imports
from itertools import combinations
from collections import OrderedDict

# Scikit Data Access imports
from .image_util import convertBinCentersToEdges

# 3rd part imports
import pandas as pd
import numpy as np
from netCDF4 import Dataset, num2date



def averageDates(dates, round_nearest_day = False):
    '''
    Compute the average of a pandas series of timestamps

    @param dates: Pandas series of pandas datetime objects
    @param round_nearest_day: Round to the nearest day

    @return Average of dates
    '''
    start = dates.min()
    newdate = (dates - start).mean() + start
    if round_nearest_day:
        newdate = newdate.round('D')
    return newdate


def dateMismatch(dates, days=10):
    '''
    Check if dates are not within a certain number of days of each other

    @param dates: Iterable container of pandas timestamps
    @param days: Number of days

    @return true if they are not with 10 days, false otherwise
    '''
    for combo in combinations(dates,2):
        if np.abs(combo[0] - combo[1]) > pd.to_timedelta(days, 'D'):
            return True
    return False

def computeEWD(grace_data, scale_factor, round_nearest_day=False):
    '''
    Compute scale corrected equivalent water depth

    Equivalent water depth by averaging results from
    GFZ, CSR, and JPL, and then applying the scale factor

    @param grace_data: Data frame containing grace data
    @param scale_factor: Scale factor to apply
    @param round_nearest_day: Round dates to nearest day

    @return Equivalent water depth determined by applying the scale factor to
            the average GFZ, JPL and CSR.
    '''

    def cutMissingData(in_data, reverse=False):
        '''
        Removes data from the beginning (or ending if reverse=True) so that
        data exists for all 3 sources (GFZ, JPL, and CSR).


        This function is necessary as not all sources may get cut when
        a starting and ending date is specified.

        @param in_data: Input grace data
        @param reverse: Remove data from end instead of beginning

        @return Tuple containing modified in_data, the last cut date
        '''

        last_cut_date = None

        if reverse==True:
            index = in_data.index[::-1]
        else:
            index = in_data.index

        for date in index:
            cut = in_data.loc[date-pd.to_timedelta('10D'):date+pd.to_timedelta('10D')]
            if min(len(cut['CSR'].dropna()), len(cut['GFZ'].dropna()), len(cut['JPL'].dropna())) == 0:
                if reverse:
                    in_data = in_data.iloc[:-1]
                else:
                    in_data = in_data.iloc[1:]

                last_cut_date = date

            else:
                break

        return in_data,last_cut_date

    # Check if there is no valid data
    if len(grace_data['CSR'].dropna()) + len(grace_data['GFZ'].dropna()) + len(grace_data['JPL'].dropna()) == 0:
        if round_nearest_day == True:
            return pd.Series(np.nan, index=grace_data.index.round('D'))
        else:
            return pd.Series(np.nan, index=grace_data.index)

    # Find all months that have different dates supplied by GFZ, JPL, and CSR
    offsets = grace_data[grace_data.isnull().any(axis=1)]

    # Starting and ending months if they don't have valid data for all 3 data sets
    offsets,cut_date1 = cutMissingData(offsets)
    offsets,cut_date2 = cutMissingData(offsets, reverse=True)

    # If beginning data has been cut, update data accordingly
    if cut_date1 != None:
        index_location = np.argwhere(grace_data.index == cut_date1)[0][0]
        new_index = grace_data.index[index_location+1]
        grace_data = grace_data.loc[new_index:]

    # If ending data has been cut, update data accordingly
    if cut_date2 != None:
        index_location = np.argwhere(grace_data.index == cut_date2)[0][0]
        new_index = grace_data.index[index_location-1]
        grace_data = grace_data.loc[:new_index]


    # Get all valid data for JPL, GFZ, and CSR
    csr = offsets['CSR'].dropna()
    gfz = offsets['GFZ'].dropna()
    jpl = offsets['JPL'].dropna()


    new_index = []
    new_measurements = []

    # Iterate over all data with offset dates and combine them
    for (c_i, c_v), (g_i,g_v), (j_i, j_v) in zip(csr.iteritems(), gfz.iteritems(), jpl.iteritems()):

        # Check if the dates are within 10 days of each other
        dates = pd.Series([c_i,g_i,j_i])
        if dateMismatch(dates):
            raise ValueError('Different dates are not within 10 days of each other')

        # Determine new index and average value of data
        new_index.append(averageDates(dates, round_nearest_day))
        new_measurements.append(np.mean([c_v, g_v, j_v]))

    # Create series from averaged results
    fixed_means = pd.Series(data = new_measurements, index=new_index)
    fixed_means.index.name = 'Date'

    # Averaging results from non mimsatched days
    ewt = grace_data.dropna().mean(axis=1)

    # If requested, round dates to nearest day
    if round_nearest_day:
        ewt_index = ewt.index.round('D')
    else:
        ewt_index = ewt.index

    # Reset ewt index
    ewt = pd.Series(ewt.as_matrix(),index = ewt_index)

    # Combined data with mismatched days with data
    # without mismatched days
    ewt = pd.concat([ewt, fixed_means])
    ewt.sort_index(inplace=True)

    # Apply scale factor
    ewt = ewt * scale_factor

    # Return results
    return ewt


def readTellusData(filename, lat_lon_list, lat_name, lon_name, data_name, data_label=None,
                   time_name=None, lat_bounds_name=None, lon_bounds_name=None,
                   uncertainty_name = None, lat_bounds=None, lon_bounds = None):
    '''
    This function reads in netcdf data provided by GRACE Tellus

    @param filename: Name of file to read in
    @param lat_lon_list: List of latitude, longitude tuples that are to be read
    @param data_label: Label for data
    @param lat_name: Name of latitude data
    @param lon_name: Name of longitude data
    @param data_name: Name of data product
    @param time_name: Name of time data
    @param lat_bounds_name: Name of latitude boundaries
    @param lon_bounds_name: Name of longitude boundaries
    @param uncertainty_name: Name of uncertainty in data set
    @param lat_bounds: Latitude bounds
    @param lon_bounds: Longitude bounds

    @return dictionary containing data and dictionary containing latitude and longitude
    '''


    def findBin(in_value, in_bounds):
        search = np.logical_and(in_value >= in_bounds[:,0], in_value < in_bounds[:,1])

        if np.sum(search) == 1:
            return np.argmax(search)
        elif in_value == in_bounds[-1]:
            return len(in_bounds)-1
        else:
            raise RuntimeError("Value not found")

    if data_label == None and time_name != None:
        raise RuntimeError("Need to specify data label when time data is used")


    if lat_bounds is None and lon_bounds is not None or \
       lat_bounds is not None and lon_bounds is None:

       raise ValueError('Must specify both lat_bounds and lon_bounds, or neither of them')

    nc = Dataset(filename, 'r')

    lat_data = nc[lat_name][:]
    lon_data = nc[lon_name][:]
    data = nc[data_name][:]


    if lat_bounds is None:
        if lat_bounds_name == None and lon_bounds_name == None:

            lat_edges = convertBinCentersToEdges(lat_data)
            lon_edges = convertBinCentersToEdges(lon_data)

            lat_bounds = np.stack([lat_edges[:-1], lat_edges[1:]], axis=1)
            lon_bounds = np.stack([lon_edges[:-1], lon_edges[1:]], axis=1)

        else:
            lat_bounds = nc[lat_bounds_name][:]
            lon_bounds = nc[lon_bounds_name][:]

    if time_name != None:
        time = nc[time_name]
        date_index = pd.to_datetime(num2date(time[:],units=time.units,calendar=time.calendar))

    if uncertainty_name != None:
        uncertainty = nc[uncertainty_name][:]


    data_dict = OrderedDict()
    meta_dict = OrderedDict()

    for lat, lon in lat_lon_list:

        # Convert lontitude to 0-360
        orig_lon = lon
        if lon < 0:
            lon += 360.



        lat_bin = findBin(lat, lat_bounds)
        lon_bin = findBin(lon, lon_bounds)

        label = str(lat) + ', ' + str(orig_lon)

        if time_name != None and uncertainty_name != None:
            frame_data_dict = OrderedDict()
            frame_data_dict[data_label] = data[:,lat_bin, lon_bin]
            frame_data_dict['Uncertainty'] = uncertainty[:,lat_bin, lon_bin]
            data_dict[label] = pd.DataFrame(frame_data_dict, index=date_index)

        elif time_name != None and uncertainty_name == None:
            data_dict[label] = pd.DataFrame({data_label : data[:, lat_bin, lon_bin]}, index=date_index)

        else:
            data_dict[label] = data[lat_bin, lon_bin]

        meta_dict[label] = OrderedDict()
        meta_dict[label]['Lat'] = lat
        meta_dict[label]['Lon'] = orig_lon



    return data_dict, meta_dict, lat_bounds, lon_bounds



def getStartEndDate(in_data):
    label, data = next(in_data.items())

    start_date = in_data.index[0]
    end_date = in_data.index[-1]

    return start_date, end_date
