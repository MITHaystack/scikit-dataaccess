# The MIT License (MIT)
# Copyright (c) 2016 Massachusetts Institute of Technology
#
# Authors: Victor Pankratius, Justin Li, Cody Rude#
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

# """@package Neveda
# Provides classes for accessing Neveda data.
# """

# mithagi required Base,Utils imports
from skdaccess.framework.data_class import DataFetcherStorage, TableWrapper
from skdaccess.utilities import pbo_util
# from skdaccess.utilities import data_util


# 3rd party package imports
import pandas as pd
import numpy as np
from tqdm import tqdm
from collections import OrderedDict


class DataFetcher(DataFetcherStorage):
    ''' 
    Data fetcher for GPS data from Neveda Geodetic Laboratory
    '''

    def __init__(self, start_date, end_date, lat_range, lon_range, mdyratio=0.7, data_type = 'ngl_gps'):
        '''
        Consctruct NGL data fetcher
        
        @param start_date: Starting date (string: '2002-01-01')
        @param end_date: Ending date (string: '2015-01-01')
        @param lat_range: Tuple containing latitude range
        @param lon_range: Tuple containing longitude range
        @param mdyratio: Choose stations whose ratio of valid/total is greater than mdyratio
        @param data_type: Either 24 hour product ('ngl_gps') or 5 minute product ('ngl_5min')
        '''
        self.start_date = start_date
        self.end_date = end_date
        self.lat_range = lat_range
        self.lon_range = lon_range
        self.mdyratio = mdyratio
        self.data_type = data_type

        super(DataFetcher, self).__init__([])

    def getStationMetadata():
        '''
        Get station metadata

        @return data frame of station metadata
        '''
        store_location = data_util.getDataLocation('ngl_gps')
        store = pd.HDFStore(store_location, 'r')
        metadata = store['metadata']
        store.close()

        metadata.loc[:,'Lon'] = (metadata.loc[:,'Lon'] + 180) % 360 - 180
        
        return metadata

    def getAntennaLogs():
        '''
        Retrieve information about antenna changes

        @return dictionary of antenna changes
        '''
        store_location = data_util.getDataLocation('ngl_gps')
        store = pd.HDFStore(store_location, 'r')
        logs_df = store['ngl_steps']
        store.close()

        metadata = DataFetcher.getStationMetadata()

        logs_dict = OrderedDict()
        
        for station in metadata.index:
            offset_dates = logs_df[logs_df['Station']==station].index.unique()
            offset_dates = pd.Series(offset_dates)
            logs_dict[station] = offset_dates

        return logs_dict
        
    def output(self):
        '''
        Construct NGL GPS data wrapper

        @return NGL GPS data wrapper
        '''

        metadata = DataFetcher.getStationMetadata()
        
        store_location = data_util.getDataLocation(self.data_type)
        store = pd.HDFStore(store_location, 'r')

        index = np.logical_and.reduce([self.lat_range[0] < metadata['Lat'],
                                       self.lat_range[1] > metadata['Lat'],
                                       self.lon_range[0] < metadata['Lon'],
                                       self.lon_range[1] > metadata['Lon']])

        region_stations = metadata[index]


        data_dict = {}

        if self.data_type == 'ngl_gps':
            valid_station_list = list(region_stations.index)
            default_columns = ('dN','dE','dU')
            default_error_columns = ('Sn','Se','Su')            
            freq = '1D'
            
        elif self.data_type == 'ngl_5min':
            store_list_tuple = set(station[6:] for station in store.keys())

            selected_station_list = set( region_stations.index )

            valid_station_list = list(store_list_tuple.intersection(store_list_tuple))
            valid_station_list.sort()

            default_columns = ('___n-ref(m)', '___e-ref(m)', '___v-ref(m)')
            default_error_columns = ('sig_n(m)', 'sig_e(m)', 'sig_v(m)')
            
            
            freq = '5min'

        min_data_len = ( (pd.to_datetime(self.start_date) - pd.to_datetime(self.end_date))
                         / pd.to_timedelta(freq) * self.mdyratio )


        for station in valid_station_list:
            data = store['data_' + station].loc[self.start_date:self.end_date]
            if len(data) >= min_data_len:
                data = data.reindex(pd.date_range(self.start_date,self.end_date,freq=freq))
                data_dict[station] = data
        

        


        metadata = metadata.loc[data_dict.keys()]
        return TableWrapper(data_dict, meta_data = metadata, default_columns = default_columns,
                            default_error_columns = default_error_columns)

        
