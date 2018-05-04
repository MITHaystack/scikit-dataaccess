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
import pandas as pd
from six.moves.urllib.request import urlopen
import numpy as np

# mithagi imports
from skdaccess.framework.data_class import DataFetcherStream, ImageWrapper
from skdaccess.utilities.modis_util import getImageType, createGrid, getFileURLs, readMODISData, getFileURLs, getFileIDs
from tqdm import tqdm


class DataFetcher(DataFetcherStream):
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
        file_urls = getFileURLs(file_ids)

        # For streaming, need to use opendap urls
        url_header = 'http://ladsweb.modaps.eosdis.nasa.gov/opendap/'
        opendap_urls = [ url_header + re.search('allData.*$',url).group(0) for url in file_urls ]
        
        # This function reads data and returns a wrapper
        return readMODISData(opendap_urls, self.variable_list, grid=self.grid, grid_fill = self.grid_fill,
                             use_long_name = self.use_long_name, platform = self.modis_platform,
                             product_id = self.modis_id)
        
