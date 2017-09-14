# The MIT License (MIT)
# Copyright (c) 2017 Massachusetts Institute of Technology
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


# Skdaccess imports
from skdaccess.framework.data_class import DataFetcherCache
from skdaccess.framework.param_class import *
from skdaccess.geo.mahali.rinex.data_wrapper import DataWrapper
from pkg_resources import resource_filename
from skdaccess.utilities.mahali_util import convert_date


# Standard library imports
from glob import glob
import shutil
import os
from six.moves.urllib.request import urlopen
import sys

# 3rd part imports
from tqdm import tqdm
import pandas as pd

class DataFetcher(DataFetcherCache):
    '''
    Data Fetcher for Mahali Data
    '''
    
    def __init__(self, ap_paramList=[], start_date=None, end_date=None, generate_links = False):
        '''
        Initialize Mahali Data Fetcher

        @param ap_paramList[stations]: Autolist of stations (Defaults to all stations)
        @param start_date: Starting date for seelcting data (Defaults to beginning of available data)
        @param end_date: Ending date for selecting data (Defaults to end of available data)
        @param generate_links: Generate links to data instead of downloading data
        '''
        
        if start_date == None:
            self.start_date = pd.to_datetime('2015232', format='%Y%j')
        else:
            self.start_date = convert_date(start_date)
                                           
                                           
        if end_date == None:
            self.end_date = pd.to_datetime('2015314', format='%Y%j')
        else:
            self.end_date = convert_date(end_date)
            
        self.date_range = pd.date_range(self.start_date, self.end_date)            
            
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


        self.generate_links = generate_links
        
        super(DataFetcher, self).__init__(ap_paramList)
            
        
    def cacheData(self):
        ''' 
        Downloads all needed data. Called by output().
        '''
        station_list = self.ap_paramList[0]()

        remote_location = '/data/mahali_UAF_data/cloud/rinex/obs'

        day_list = []

        start_year = self.start_date.strftime('%Y')
        start_day = self.start_date.strftime('%j')

        end_year = self.end_date.strftime('%Y')
        end_date = self.end_date.strftime('%j')   
    
        data_list = pd.DataFrame(columns=['Site','Date'])
        
        # Get a list of all data that needs to be loaded
        mahali_data_info_location = resource_filename('skdaccess',os.path.join('support','mahali_data_info.hdf'))
        for station in station_list:
            
            try:
                available_dates = pd.read_hdf(mahali_data_info_location, station)
            except KeyError:
                print('Unknown station:',station, )

            common_dates = list(set(self.date_range).intersection(set(available_dates)))

            common_dates.sort()

            data_list = pd.concat([data_list, pd.DataFrame({'Site':station,'Date':common_dates})])
                
                
        
        # Get a list of all needed filenames
        data_list_obs = data_list.Site + data_list.Date.apply(lambda x: x.strftime('%j0.%yo'))
        data_list_nav = data_list.Site + data_list.Date.apply(lambda x: x.strftime('%j0.%yn'))
        
        data_set_filenames = set(pd.concat([data_list_obs, data_list_nav]))

        
        # Get locations of all files to download
        def getFileLocation(in_file):
            day = in_file[4:7]
            if in_file[-1] == 'n':
                data_folder = 'nav'
            elif in_file[-1] == 'o':
                data_folder = 'obs'
            else:
                raise ValueError('Could not parse in_file')

            return 'rinex/' + data_folder + '/2015/' + day + '/' + in_file



        # Key function to sort rinex files by date, then
        # station, then type (NAV or OBS)
        key_func = lambda x: x[-3:-1] + x[-8:-5] + x[-12:-8] + x[-1]

        # Base url of data
        base_url = 'http://apollo.haystack.mit.edu/mahali-data/'
        

        # Download files to disk
        if not self.generate_links:
            data_location = DataFetcher.getDataLocation('mahali_rinex')

            if data_location == None:
                data_location = os.path.join(os.path.expanduser('~'), '.skdaccess','mahali_rinex')
                os.makedirs(data_location, exist_ok=True)

            # Get currently downloaded files
            file_list = glob(os.path.join(data_location,'*.*n',)) + glob(os.path.join(data_location,'*.*o',))
            file_list = set(file.split(os.sep)[-1] for file in file_list)

            # Select files that are wanted but not yet downloaded
            missing_files = data_set_filenames.difference(file_list)

            missing_files = list(missing_files)
            missing_files.sort()
            file_location_list = [getFileLocation(filename) for filename in missing_files]


            if len(file_location_list) > 0:
                print('Downloading mahali data')
                sys.stdout.flush()
                for url_path, filename in tqdm(zip(file_location_list, missing_files), total=len(missing_files)):
                    with  open(os.path.join(data_location, filename), 'wb') as data_file:
                        shutil.copyfileobj(urlopen(base_url+ url_path), data_file)

            # return the appropriate list of files to load

            obs_file_list = [os.path.join(data_location, file) for file in data_list_obs]
            nav_file_list = [os.path.join(data_location, file) for file in data_list_nav]

        
        # Not downloading data, just generating links to where data is located
        else:
            obs_file_list = [base_url + getFileLocation(location) for location in data_list_obs]
            nav_file_list = [base_url + getFileLocation(location) for location in data_list_nav]


        obs_file_list.sort(key=key_func)
        nav_file_list.sort(key=key_func)

        return nav_file_list, obs_file_list
                
    def output(self):
        ''' 
        Generate data wrapper for Mahali data

        @return Mahali data wrapper
        '''
        nav_files, obs_files = self.cacheData()
        
        def getSiteAndDate(in_filename):
            date = pd.to_datetime('2015' + in_filename[-8:-5], format='%Y%j')
            return in_filename[-12:-8], date
  
        
        data_list = []
        for nav, obs in zip(nav_files, obs_files):
            site, date = getSiteAndDate(nav)
            
            if (site,date) != getSiteAndDate(obs):
                raise RuntimeError('Data mismatch')
                
            # data_list.append([site,date,readRinexNav(nav), rinexobs(obs)])
            data_list.append([site,date,nav, obs])
        
        return DataWrapper(data_list)
