# The MIT License (MIT)
# Copyright (c) 2017 Massachusetts Institute of Technology
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


# Skdaccess imports
from skdaccess.framework.data_class import DataFetcherCache, TableWrapper
from skdaccess.framework.param_class import *
from pkg_resources import resource_filename
from skdaccess.utilities.mahali_util import convert_date, parseIonoFile
from skdaccess.utilities.support import retrieveCommonDatesHDF

# Standard library imports
from urllib import parse
from collections import OrderedDict
from collections import defaultdict
from itertools import repeat

# 3rd party imports
from tqdm import tqdm
import pandas as pd

class DataFetcher(DataFetcherCache):
    '''
    Data Fetcher for Mahali Data
    '''
    
    def __init__(self, ap_paramList=[], start_date=None, end_date=None):
        '''
        Initialize Mahali Data Fetcher

        @param ap_paramList[stations]: Autolist of stations (Defaults to all stations)
        @param start_date: Starting date for seelcting data (Defaults to beginning of available data)
        @param end_date: Ending date for selecting data (Defaults to end of available data)
        '''

        # Get start date
        if start_date == None:
            self.start_date = pd.to_datetime('2015275', format='%Y%j')
        else:
            self.start_date = convert_date(start_date)
                                           
        # Get end date
        if end_date == None:
            self.end_date = pd.to_datetime('2015307', format='%Y%j')
        else:
            self.end_date = convert_date(end_date)
            
        self.date_range = pd.date_range(self.start_date, self.end_date)            

        # Set station list if none is given
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
            
    def output(self):
        ''' 
        Generate data wrapper for Mahali tec data

        @return Mahali data wrapper
        '''

        def generatePath(base_url, station, in_date):
            '''
            Generate path to file based on station, date, and base url

            @param base_url: Base url to put in front of generated url
            @param station: Name of station
            @param in_date: Date of data to create path for

            @return The url for the station data
            '''
            year = in_date.strftime('%Y')
            day = in_date.strftime('%j')
            date = in_date.strftime('%Y%m%d')

            path = 'tec/{year}/{day}/{station}-{date}.iono.gz'.format(year=year,
                                                                      day=day,
                                                                      station=station,
                                                                      date=date)
            return parse.urljoin(base_url, path)
            

        # Get station lists
        station_list = self.ap_paramList[0]()

        # Retrieve dates containing data for station list
        available_data_dict = retrieveCommonDatesHDF('mahali_tec_info.hdf', station_list, self.date_range)

        # Location of data
        base_url = 'http://apollo.haystack.mit.edu/mahali-data/'
        url_list = []

        # Generate url list
        for station, dates in available_data_dict.items():
            url_list += list(map(generatePath, repeat(base_url), repeat(station), dates))


        # Cache data
        file_list = self.cacheData('mahali_tec', url_list)

        # Dictionary to hold parsed data
        parsed_data_dict = defaultdict(list)

        # Parse data
        for filename in file_list:
            station = filename[-21:-17]
            parsed_data_dict[station].append(parseIonoFile(filename))

        
        # combine data frames for each station into a single 
        combined_data_dict = OrderedDict()

        for station,data in parsed_data_dict.items():
            combined_data_dict[station] = pd.concat(data)

        # Return data wrapper
        return TableWrapper(combined_data_dict, default_columns=['vertical_tec'])
    

        


        
