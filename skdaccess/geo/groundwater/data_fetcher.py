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

# """@package Groundwater
# Provides classes for accessing Groundwater data.
# """

# mithagi required Base imports
from skdaccess.framework.data_class import DataFetcherStorage, TableWrapper, SeriesWrapper


# Python Standard Library
from collections import OrderedDict
import re
import os
from six.moves.urllib.error import HTTPError
from six.moves.urllib.request import urlopen
from shutil import copyfileobj
from io import StringIO

# 3rd party package imports
import pandas as pd
import numpy as np


class DataFetcher(DataFetcherStorage):
    '''
    Generates Data Wrappers of groundwater measurements taken in the US
    '''
    def __init__(self,  ap_paramList = [], start_date = None, end_date = None, cutoff=0.75):
        ''' 
        Construct a Groundwater Data Fetcher

        @param ap_paramList[LowerLat]: Autoparam Lower latitude
        @param ap_paramList[UpperLat]: Autoparam Upper latitude
        @param ap_paramList[LeftLon]: Autoparam Left longitude
        @param ap_paramList[RightLon]: Autoparam Right longitude
        @param start_date: Starting date (defualt: None)
        @param end_date: Ending date (default: None)
        @param cutoff: Required amount of data for each station
        '''



        self.start_date   = pd.to_datetime(start_date)
        self.end_date     = pd.to_datetime(end_date)
        self.ap_paramList = ap_paramList
        self.cutoff = cutoff

    def output(self):
        ''' 
        Fetch Groundwater Data Wrapper

        @return Groundwater Data Wrapper
        '''
        
        meta_data = DataFetcher.getStationMetadata()
        
        data_file    = DataFetcher.getDataLocation('groundwater')
        if data_file is None:
            print("No data available")
            return None

        if len(self.ap_paramList) == 1:
            station_list = self.ap_paramList[0]()            
        elif len(self.ap_paramList) == 4:
            llat = self.ap_paramList[0]()
            ulat = self.ap_paramList[1]()            
            llon = self.ap_paramList[2]()                        
            rlon = self.ap_paramList[3]()            



            
            station_index = np.logical_and.reduce([meta_data.Lat > llat, meta_data.Lat < ulat,
                                                   meta_data.Lon > llon, meta_data.Lon < rlon])

            cut_metadata = meta_data[station_index]
            station_list = cut_metadata[cut_metadata['Data Available'] == 1].index.tolist()

        else:
            station_list = None


        data_dict = OrderedDict()
        store = pd.HDFStore(data_file, 'r')


        if station_list == None:
            stations = [str(site) for site in meta_data[meta_data['Data Available']==1].index]

        else:
            stations = station_list

        for station in stations:
            if self.start_date != None and self.end_date != None:
                data = store['USGS' + str(station)].reindex(pd.date_range(self.start_date, self.end_date))
            else:
                data = store['USGS' + str(station)]
            if len(data.dropna()) / len(data) >= self.cutoff:
                data_dict[int(station)] = data
                
        store.close()

        return(TableWrapper(data_dict, meta_data=meta_data, default_columns=['Median Depth to Water']))

    def __str__(self):
        '''
        String representation of data fetcher

        @return string describing data fetcher
        '''
        return 'Ground Water Data Fetcher' + super(DataFetcher, self).__str__()


    def getStationMetadata():
        '''
        Retrieve metadata on groundwater wells

        @return pandas dataframe with groundwater well information
        '''
            
        data_file = DataFetcher.getDataLocation('groundwater')
        if data_file is None:
            print('Dataset not available')
            return None

        store = pd.HDFStore(data_file,'r')
        meta_data = store['meta_data']
        store.close()

        
        return meta_data

    @classmethod
    def downloadFullDataset(cls, out_file = 'gw.h5', use_file = None):
        '''
        Download and parse US groundwater data provided by USGS

        @param out_file: Output filename for parsed data
        @param use_file: Specify the directory where the data is.
                         If None, the function will download the data

        @return Absolute path of parsed data
        '''
        # Function that converts a string to a float
        def convert_to_float(x):
            try:
                return np.float(x)
            except:
                return np.nan

        # Function to test if a string can
        # be converted to a float
        def is_valid_number(x):
            try:
                test = np.float(x)
                return True
            except:
                return False

        # Returns 'No comment' for strings that
        # can be interpreted as a float,
        # and returns the string if it can't
        # be interpreted as a float
        def comment(x):
            try:
                test = np.float(x)
                return 'No comment'
            except:
                return x        

        # Abbreviations of all 50 states
        state_list = ['AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
                      'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
                      'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
                      'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
                      'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY']

        full_meta_data = None
        # temporary data storage 
        data_dict = OrderedDict()

        data_filename_list = []
        metadata_filename_list = []

        for state in state_list:
            data_filename = state + '_gw_data.rdb'
            metadata_filename = state + '_gw_metadata.rdb'
            if use_file is None:

                print("Downloading", state, "data")


                data_file = open(data_filename, 'wb')
                metadata_file = open(metadata_filename, 'wb')
                try:
                    # Download data
                    copyfileobj(urlopen('http://waterservices.usgs.gov/nwis/dv/?format=rdb&stateCd=' + state +
                                        '&startDT=1800-01-01&endDT=2020-12-31&statCd=00003,00008&parameterCd=72019&siteType=GW'),
                                data_file)
                    data_file.close()


                    # Download meta data
                    copyfileobj(urlopen('http://waterservices.usgs.gov/nwis/site/?format=rdb&stateCd=' + state +
                                        '&startDT=1800-01-01&endDT=2020-12-31&parameterCd=72019&siteType=GW&hasDataTypeCd=dv'),
                                metadata_file)


                except HTTPError:
                    print('No data for', state)


                finally:
                    data_file.close()
                    metadata_file.close()

            else:
                data_filename = use_file + data_filename
                metadata_filename = use_file + metadata_filename

            # store data filename and metadata filename
            data_filename_list.append(data_filename)
            metadata_filename_list.append(metadata_filename)

        for data_filename, metadata_filename, state_abbrev in zip(data_filename_list, metadata_filename_list, state_list):

            print("Processing ", state_abbrev, ': ', data_filename, sep='')

            #Read metadata
            meta_data = pd.read_table(metadata_filename, skiprows=31, names = ['Agency', 'Site Number', 'Site Name', 'Site Type', 
                                                                               'Lat', 'Lon', 'LatLon Accuracy', 'LatLon Datum',
                                                                               'Altitude', 'Altitude Accuracy', 'Altitude Datum',
                                                                               'Hydrologic Code'], index_col=1)

            meta_data['Data Available'] = int(0)
            meta_data['State'] = state_abbrev

            full_lines = open(data_filename).read().splitlines()

            # Get the line number of the header lines
            header_nums = []
            for line_num, line in enumerate(full_lines):
                if re.match('agency_cd', line):
                    header_nums.append(line_num)


            # temporary storage for combine type
            type_dict = OrderedDict()


            # Read in all the data based on the header lines
            for header_num in header_nums:
                # Check to make sure there is valid data
                if len(full_lines[header_num].split()) < 5:
                    print('No median or averages available for', data_filename)
                    continue


            
                
                start = header_num+2
                end = len(full_lines)
                for line_num, line in enumerate(full_lines[start:],start):
                    if line[0] == '#':
                        end = line_num
                        break

                # If both median and average present
                if len(full_lines[header_num].split()) > 5:
                    in_data = pd.read_table(StringIO('\n'.join(full_lines[start:end])), header=None,
                                                names=['Agency','Site ID','Date','Mean Depth to Water','Mean Quality',
                                                       'Median Depth to Water', 'Median Quality'],
                                                index_col=2, parse_dates=True)
                    
                    in_data.loc[:,'Mean Comment'] = in_data.loc[:,'Mean Depth to Water'].apply(comment)
                    in_data.loc[:,'Median Comment'] = in_data.loc[:,'Median Depth to Water'].apply(comment)

                    in_data.loc[:,'Mean Depth to Water'] = in_data.loc[:,'Mean Depth to Water'].apply(convert_to_float)         

                    in_data.loc[:,'Median Depth to Water'] = in_data.loc[:,'Median Depth to Water'].apply(convert_to_float)         

                # All the data is either median or mean
                else:
                    if full_lines[header_num].split()[3][-5:] == '00008':
                        data_name = 'Median Depth to Water'
                        comment_name = 'Median Comment'
                        quality_name = 'Median Quality'
                    elif full_lines[header_num].split()[3][-5:] == '00003':
                        data_name = 'Mean Depth to Water'
                        comment_name = 'Mean Comment'
                        quality_name = 'Mean Quality'
                    else:
                        raise ValueError('Data type not understood')

                    
                    in_data = pd.read_table(StringIO('\n'.join(full_lines[start:end])), header=None,
                                                names=['Agency','Site ID','Date', data_name, quality_name],
                                                index_col=2, parse_dates=True)

                    in_data.loc[:,comment_name] = in_data.loc[:, data_name].apply(comment)
                    in_data.loc[:,data_name] = in_data.loc[:, data_name].apply(convert_to_float)



                # Data has been read in, now determine
                # combine type and store results in
                # data_dict and type_dict
                site_id = in_data.ix[0,'Site ID']
                in_data.drop('Site ID', 1,inplace=True)

                data_dict[site_id] = in_data

                meta_data.loc[site_id, 'Data Available'] = 1


            if not data_dict:
                print('No valid wells for', data_filename)
                continue


            full_meta_data = pd.concat([full_meta_data, meta_data])



        store = pd.HDFStore(out_file, complevel=5, complib='blosc')
        for site,data in data_dict.items():
            store.put('USGS' + str(site), data, format='table')


        store.put('meta_data',full_meta_data,format='table')
        store.close()

        DataFetcher.setDataLocation('groundwater', os.path.abspath(out_file))

        
