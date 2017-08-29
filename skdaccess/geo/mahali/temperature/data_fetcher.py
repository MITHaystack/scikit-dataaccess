# The MIT License (MIT)
# Copyright (c) 2017 Massachusetts Institute of Technology
#
# Authors: Cody Rude, Dave Blair
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


# Skdaccess imports
from skdaccess.framework.data_class import DataFetcherStream, TableWrapper
from skdaccess.framework.param_class import *
from skdaccess.utilities.mahali_util import convert_date
from pkg_resources import resource_filename


# Standard library imports
from glob import glob
import shutil
import os
import json
from collections import OrderedDict

# 3rd part imports
from six.moves.urllib.request import urlopen
from tqdm import tqdm
import pandas as pd
import numpy as np

class DataFetcher(DataFetcherStream):
    '''
    Data Fetcher for Mahali temperature data
    '''
    
    def __init__(self, ap_paramList=[], start_date=None, end_date=None):
        '''
        Initialize Mahali temperature data fetcher

        @param ap_paramList[stations]: Autolist of stations (Defaults to all stations)
        @param start_date: Starting date for seelcting data (Defaults to beginning of available data)
        @param end_date: Ending date for selecting data (Defaults to end of available data)
        '''
        
        if start_date == None:
            self.start_date = pd.to_datetime('2015271', format='%Y%j')
        else:
            self.start_date = convert_date(start_date)
                                           
                                           
        if end_date == None:
            self.end_date = pd.to_datetime('2015315', format='%Y%j')
        else:
            self.end_date = convert_date(end_date)
            
        if len(ap_paramList) == 0:
            station_list = [
                'mh02',
                'mh03',
                'mh04',
                'mh05',
                'mh06',
                'mh07',
                'mh08',
                'mh09',
                'mh13',
            ]
            ap_paramList = [ AutoList(station_list) ]
        
        super(DataFetcher, self).__init__(ap_paramList)



    def retrieveOnlineData(self, data_specification):
        '''
        Load data in from a remote source

        @param data_specification: Pandas dataframe containing the columns 'station', 'date', and 'filename'

        @return Ordered dictionary for each station (key) which cointains a pandas data frame of the temperature
        '''

        # Location of data depot
        url = 'http://apollo.haystack.mit.edu/mahali-data/'

        locations = (  url
                     + 'metadata/' 
                     + data_specification['station'] 
                     + '/logs/sensor/'
                     + data_specification['date'].apply(lambda x: x.strftime('%Y%j'))
                     + '/'
                     + data_specification['filename'] ).tolist()
        

        
        # Data will go into this dictionary as {station: [(time, measurement), (time2, measurement2), ...]}
        all_temperature_data = OrderedDict()

        # Parse jsonl files
        for station, location in zip(data_specification['station'], locations):
            with urlopen(location) as this_json_file:
                # Encased in a try/except because of lines full of junk
                # (e.g. the last line of metadata/mh02/logs/sensor/2015277/sensor@2015-10-04T225240Z_1443999160.jsonl)

                try:
                    for line in this_json_file:
                        line_data = json.loads(line)
                        this_time = pd.to_datetime(line_data['time'])
                        this_temp = float(line_data["event_data"]["data"])

                        # If data for that station already exists
                        try:
                            all_temperature_data[station].append([this_time, this_temp])
                        # If there's no existing entry for that station
                        except KeyError:
                            all_temperature_data[station] = [ [this_time, this_temp] ]
                except ValueError:
                    pass


        for station in all_temperature_data.keys():
            all_temperature_data[station] = pd.DataFrame(all_temperature_data[station], columns=['Time','Temperature']).set_index('Time')
                
        return all_temperature_data
        
    def output(self):
        ''' 
        Generate data wrapper for Mahali temperatures

        @return Mahali temperature data wrapper
        '''

        # Function to extract date from filename (only month/day/year, no hours/minutes/seconds)
        def toDateTime(in_filename):
            return pd.to_datetime(pd.to_datetime(in_filename[7:25]).strftime('%Y-%m-%d'))


        # Read in file list:
        mahali_temperature_info = resource_filename('skdaccess', os.path.join('support','mahali_temperature_info.txt'))
        filenames = pd.read_csv(mahali_temperature_info,header=None,
                                names=('station','filename'),
                                skipinitialspace=True)


        # Create a columns of dates
        filenames['date'] = filenames['filename'].apply(toDateTime)

        # Need to grab day before as data can spill over
        adjusted_start_date = self.start_date - pd.to_timedelta('1d')
        adjusted_end_date = self.end_date + pd.to_timedelta('1d')


        station_list = self.ap_paramList[0]()
        # Get data for each selected station one day before until one day afte requested date
        index_to_retrieve = np.logical_and.reduce([filenames.loc[:, 'station'].apply(lambda x: x in station_list),
                                                   filenames.loc[:, 'date'] >= adjusted_start_date,
                                                   filenames.loc[:, 'date'] <= self.end_date])

        all_temperature_data = self.retrieveOnlineData(filenames[index_to_retrieve])

        # Due to data spillover, cut each data frame in dictionary
        for station in all_temperature_data.keys():
            all_temperature_data[station] = all_temperature_data[station].loc[adjusted_start_date:adjusted_end_date]

        # Return table wrapper of data
        return TableWrapper(all_temperature_data, default_columns = ['Temperature'])
