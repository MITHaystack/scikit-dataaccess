# The MIT License (MIT)
# Copyright (c) 2016 Massachusetts Institute of Technology
#
# Authors: Victor Pankratius, Justin Li, Cody Rude
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

"""@package Groundwater
Provides classes for accessing Groundwater data.
"""

# mithagi required Base imports
from skdaccess.framework.data_class import DataFetcherBase, DataPanelWrapper
from skdaccess.utilities.data_util import getDataLocation
from skdaccess.geo.groundwater.data_wrapper import DataWrapper

# 3rd party package imports
import pandas as pd



class DataFetcher(DataFetcherBase):
    '''
    Generates Data Wrappers of groundwater measurements taken in California
    '''
    def __init__(self,  ap_paramList = [], start_date = None, end_date = None, cutoff=0.75, adjust_heights = False, wrapper_type='series'):
        ''' 
        Construct a Ground Water Data Fetcher

        @param ap_paramList[station_list]: List of stations (Optional)
        @param start_date: Starting date (defualt: None)
        @param end_date: Ending date (default: None)
        @param cutoff: Specified required amount of data at a station
        @param adjust_heights: Flag to indicate going to water height, instead of original depth to water
        @param wrapper_type: Select the type of iterator wrapper to generate, as series or table
        '''
        self.meta_data = DataFetcher.getStationMetadata()

        self.start_date   = pd.to_datetime(start_date)
        self.end_date     = pd.to_datetime(end_date)
        self.ap_paramList = ap_paramList
        self.cutoff = cutoff
        self.adjust_heights = adjust_heights
        self.wrapper_type = wrapper_type

    def output(self):
        ''' 
        Generate Groundwater Data Wrapper

        @return Groundwater Data Wrapper
        '''

        data_file    = getDataLocation('groundwater')
        if data_file is None:
            print("No data available")
            return None


        if self.ap_paramList == []:
            station_list = []
        else:
            station_list = self.ap_paramList[0]()



        data_dict = dict()
        store = pd.HDFStore(data_file, 'r')

        if len(station_list) == 0:
            stations = [station[5:] for station in store.keys() if station != '/meta_data']

        else:
            stations = station_list

        for station in stations:
            if self.start_date != None and self.end_date != None:
                data = store['USGS' + str(station)].reindex(pd.date_range(self.start_date, self.end_date))
            else:
                data = store['USGS' + str(station)]
            if len(data.dropna()) / len(data) > self.cutoff:
                if self.adjust_heights == False:
                    data_dict[str(station)] = data
                else:
                    altitude = self.meta_data.loc[int(station), 'Altitude']
                    # altitude_unc = self.meta_data.loc[int(station), 'AltitudeAccuracy']
                    data.loc[:, 'Water Depth'] = altitude - data.loc[:, 'Water Depth']
                    # data.loc[:, 'Uncertainty'] = data.loc[:,'Uncertainty']
                    data_dict[str(station)] = data
                
        store.close()

        if self.wrapper_type == 'series':
            data = DataWrapper(pd.Panel.from_dict(data_dict,orient='minor'), self.meta_data)
            return data
        elif self.wrapper_type == 'table':
            return(DataPanelWrapper(pd.Panel.from_dict(data_dict,orient='minor'), meta_data=self.meta_data))
        else:
            print('... Invald wrapper type, defaulting to series ...')
            data = DataWrapper(pd.Panel.from_dict(data_dict,orient='minor'), self.meta_data)
            

    def __str__(self):
        '''
        String representation of data fetcher

        @return string describing data fetcher
        '''
        return 'Ground Water Data Fetcher' + super(DataFetcher, self).__str__()


    def getStationMetadata():
        data_file = getDataLocation('groundwater')
        if data_file is None:
            print('Dataset not available')
            return None

        store = pd.HDFStore(data_file,'r')
        meta_data = store['meta_data']
        store.close()
        
        return meta_data
