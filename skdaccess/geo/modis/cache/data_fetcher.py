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

# """@package MODIS data
# Provides classes for accessing MODIS data.
# """

# Standard library imports
from collections import OrderedDict
from pathlib import Path
from shutil import copyfileobj
import os
import re


# 3rd party package imports
import numpy as np
import pandas as pd
from six.moves.urllib.request import urlopen

# mithagi imports
from skdaccess.framework.data_class import DataFetcherCache, ImageWrapper
from skdaccess.utilities.modis_util import getImageType, createGrid, getFileURLs, readMODISData, getFileURLs, getFileIDs
from tqdm import tqdm


class DataFetcher(DataFetcherCache):
    ''' Data Fetcher for MODIS data '''

    def __init__(self, ap_paramList, modis_platform, modis_id, variable_list, start_date, end_date,
                 daynightboth = 'D', grid=None, grid_fill = np.nan, use_long_name=False):

        '''
        Construct Data Fetcher object

        @param ap_paramList[lat]: Search latitude
        @param ap_paramList[lon]: Search longitude
        @param modis_platform: Platform (Either "Terra" or "Aqua")
        @param modis_id: Product string (e.g. '06_L2')
        @param variable_list: List of variables to fetch
        @param start_date: Starting date
        @param end_date: Ending date
        @param daynightboth: Use daytime data ('D'), nighttime data ('N') or both ('B')
        @param grid: Further divide each image into a multiple grids of size (y,x)
        @param grid_fill: Fill value to use when creating gridded data
        @param use_long_name: Use long names for metadata instead of variable name
        '''



        self.modis_id = modis_id
        self.variable_list = variable_list
        self.start_date = start_date
        self.end_date = end_date
        self.daynightboth = daynightboth
        self.grid = grid
        self.grid_fill = grid_fill
        self.use_long_name = use_long_name


        if modis_platform.lower() == 'terra':
            self.modis_platform = 'MOD'
        elif modis_platform.lower() == 'aqua':
            self.modis_platform = 'MYD'
        else:
            raise ValueError('Did not understand modis platform')

        self.modis_identifier = self.modis_platform + modis_id

        super(DataFetcher, self).__init__(ap_paramList)


    def find_data(self, fileid_list):
        '''
        Finds files previously downloaded files associated with fileids

        @param fileid_list: List of file id's
        @return Pandas series of file locaitons indexed by file id
        '''

        data_location = DataFetcher.getDataLocation('modis')

        file_locations = []
        if data_location != None:
            try:
                metadata = pd.read_csv(os.path.join(data_location,'metadata.csv'), index_col=0)
                for fileid in fileid_list:
                    if fileid in metadata.index:
                        file_locations.append(metadata.loc[fileid,'filename'])

                    else:
                        file_locations.append(None)

            except OSError:
                file_locations = [ None for i in range(len(fileid_list)) ]

        else:
            file_locations = [ None for i in range(len(fileid_list)) ]


        return pd.Series(file_locations, index=fileid_list)
        
 
    def cacheData(self, data_specification):
        '''
        Download MODIS data

        @param data_specification: List of file IDs to cache
        '''
        file_ids = data_specification

        def download_data(missing_metadata):
            data_location = DataFetcher.getDataLocation('modis')

            if data_location == None:
                data_location = os.path.join(os.path.expanduser('~'), '.skdaccess','modis')
                os.makedirs(data_location, exist_ok=True)
                DataFetcher.setDataLocation('modis', data_location)

            try:
                metadata = pd.read_csv(os.path.join(data_location, 'metadata.csv'), index_col=0)

            except OSError:
                metadata = pd.DataFrame(columns=["filename"])
                metadata.index.name = 'fileid'


            fileid_list = list(missing_metadata.index)
            file_urls = getFileURLs(fileid_list)

            filename_list = []
            for fileid, fileurl in tqdm(zip(fileid_list, file_urls), total=len(fileid_list)):
                filename = re.search('[^/]*$', fileurl).group()

                data_file = open(os.path.join(data_location,filename), 'wb')
                copyfileobj(urlopen(fileurl), data_file)
                data_file.close()
                metadata.loc[fileid] = filename
                filename_list.append(filename)

            metadata.to_csv(os.path.join(data_location, 'metadata.csv'))

            for fileid, filename in zip(fileid_list, filename_list):
                missing_metadata.loc[fileid] = filename

            return missing_metadata


        file_names = self.find_data(file_ids)


        missing = file_names[pd.isnull(file_names)]

        if len(missing) > 0:
            downloaded = download_data(missing)

    def output(self):
        ''' 
        Generate data wrapper
        
        @return data wrapper of MODIS data
        '''

        # Determine latitude and longitude for
        # output
        lat = self.ap_paramList[0]()
        lon = self.ap_paramList[1]()


        start_date = self.start_date
        end_date = self.end_date
        time = self.daynightboth

        file_ids = getFileIDs(self.modis_identifier, start_date, end_date, lat, lon, time)
        
        self.cacheData(file_ids)

        file_list = self.find_data(file_ids)

        # Location of data files
        data_location = DataFetcher.getDataLocation('modis')

        # Generate list containing full paths to data files
        file_locations = []
        for filename in file_list:
            file_locations.append(os.path.join(data_location, filename))

        # This function reads data and returns a wrapper
        return readMODISData(file_locations, self.variable_list, grid=self.grid, grid_fill = self.grid_fill,
                             use_long_name = self.use_long_name, platform = self.modis_platform,
                             product_id = self.modis_id)
        
