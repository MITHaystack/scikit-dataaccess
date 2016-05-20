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

"""@package GRACE
Provides classes for accessing GRACE data.
"""

# mithagi required Base imports
from skdaccess.framework.data_class import DataFetcherBase, DataPanelWrapper
from skdaccess.geo.grace.data_wrapper import DataWrapper
from skdaccess.utilities.data_util import getDataLocation

# 3rd party package imports
import pandas as pd
import numpy as np

class DataFetcher(DataFetcherBase):
    ''' Data Fetcher for GRACE data '''

    def __init__(self, ap_paramList, start_date = None, end_date = None, resample = True, wrapper_type='series'):
        '''
        Construct a Grace Data Fetcher

        @param ap_paramList[geo_pont]: Geographic location of grace data to select
        @param start_date: Beginning date
        @param end_date: Ending date
        @param resample: Resample the data to daily resolution, leaving NaN's in days without data (Default True)
        @param wrapper_type: Select the type of iterator wrapper to generate, as series or table
        '''
        
        self.start_date = start_date
        self.end_date = end_date
        self.resample = resample
        self.wrapper_type = wrapper_type
        super(DataFetcher, self).__init__(ap_paramList)
        
    def output(self):
        ''' 
        Create data wrapper of grace data for specified geopoint.

        @return Grace Data Wrapper
        '''

        data_file = getDataLocation('grace')
        if data_file is None:
            print("No data available")
            return None
        
        geo_point = self.ap_paramList[0]()
        store = pd.HDFStore(data_file, 'r')

        # Get appropriate time range
        start_date = self.start_date
        end_date = self.end_date

        if start_date == None:
            start_date = store['grace'].keys()[0]

        elif type(start_date) == str:
            start_date = pd.to_datetime(start_date)


        if end_date == None:
            end_date = store['grace'].keys()[-1]

        elif type(end_date) == str:
            end_date == pd.to_datetime(end_date)
        
        
        data = store['grace'][start_date:end_date]
        unc = store['uncertainty']
        store.close()

        lat = geo_point[0]
        lon = geo_point[1] + 360

        lat_index = round(lat - (lat % 1)) + 0.5
        lon_index = round(lon - (lon % 1)) + 0.5

        grace_data = data.loc[:,lat_index, lon_index]
        grace_data.name = 'Grace'

        grace_unc = unc.loc[lat_index, lon_index]
        grace_unc = pd.Series(np.ones(len(grace_data)) * grace_unc, index=grace_data.index,name="Uncertainty")
        grace_data = pd.concat([grace_data, grace_unc], axis=1)

        if self.resample == True:
            grace_data = grace_data.reindex(pd.date_range(start_date, end_date))

        if self.wrapper_type == 'series':
            return(DataWrapper(grace_data))
        elif self.wrapper_type == 'table':
            grace_data.columns = ['Equivalent Water Thickness (cm)', 'Uncertainty']
            return(DataPanelWrapper(pd.Panel.from_dict({'GRACE':grace_data},orient='minor')))
        else:
            print('... Invald wrapper type, defaulting to series ...')
            return(DataWrapper(grace_data))
            

    def __str__(self):
        '''
        String representation of data fetcher

        @return String listing the name and geopoint of data fetcher
        '''
        return 'Grace Data Fetcher' + super(DataFetcher, self).__str__()
