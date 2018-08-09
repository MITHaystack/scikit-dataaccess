# The MIT License (MIT)
# Copyright (c) 2018 Massachusetts Institute of Technology
#
# Author: Cody Rude
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

# Scikit Data Access imports
from skdaccess.framework.data_class import DataFetcherCache, ImageWrapper
from skdaccess.utilities.support import convertToStr
from skdaccess.utilities.sentinel_1_util import parseSatelliteData

# 3rd party imports
import pandas as pd
import numpy as np
from osgeo import gdal

# Standard library imports
from collections import OrderedDict
from calendar import monthrange
from zipfile import ZipFile
import xml.etree.ElementTree as ET
from scipy.constants import c
import os


class DataFetcher(DataFetcherCache):
    ''' DataFetcher for retrieving Sentinel SLC data '''
    def __init__(self, url_list, satellite_url_list, username, password, swath, polarization = 'VV', local_paths=False, verbose=True):
        '''
        Initialize Sentinel Data Fetcher

        @param url_list: List of urls of SLC data
        @param satellite_url_list: List of satellite urls
        @param username: Username for downloading data
        @param password: Password for downloading data
        @param swath: Swath number (1, 2, or 3)
        @param polarization: Polarization of data to retrieve
        @param local_paths: locations are local paths, not urls
        @param verbose: Print additional information
        '''

        self.url_list = url_list
        self.satellite_url_list = satellite_url_list
        self.swath = swath
        self.username = username
        self.password = password
        self.polarization = polarization
        self.local_paths = local_paths

        super(DataFetcher, self).__init__(verbose=verbose)

    def output(self):
        '''
        Generate data wrapper

        @return Sentinel SLC data in a data wrapper
        '''

        # Check that the number of images matches the number of orbit files
        num_images = len(self.url_list)
        if num_images != len(self.satellite_url_list):
            raise ValueError('Different number of slc and satellite urls')


        if not self.local_paths:

            self.verbose_print('Retrieving SLC data', flush=True)
            file_list = self.cacheData('sentinel_1', self.url_list, self.username, self.password,
                                       use_requests=True, use_progress_bar=self.verbose)
            self.verbose_print('Retrieving orbit files', flush=True)
            satellite_file_list = self.cacheData('sentinel_1', self.satellite_url_list, self.username, self.password,
                                                 use_requests=True, use_progress_bar=self.verbose)
            self.verbose_print('All files retrieved', flush=True)
        else:
            file_list = self.url_list
            satellite_file_list = self.satellite_url_list

        metadata = OrderedDict()

        data_dict = OrderedDict()

        for index, (filepath, satellite_filepath) in enumerate(zip(file_list, satellite_file_list)):

            filename = os.path.split(filepath)[1]
            filename_unzipped = filename[:-3] + 'SAFE'

            gdal_path = '/vsizip/' + os.path.join(filepath, filename_unzipped) + ':IW' + convertToStr(self.swath) + '_' + self.polarization

            dataset = gdal.Open('SENTINEL1_DS:' + gdal_path)

            metadata_filename = os.path.split(dataset.GetFileList()[1])[-1]

            metadata[filename] = OrderedDict()
            with ZipFile(filepath, 'r') as zipped_file:
                metadata[filename]['Tree'] = ET.parse(zipped_file.open(os.path.join(filename_unzipped, 'annotation', metadata_filename)))

            radar_freq = float(metadata[filename]['Tree'].find('generalAnnotation/productInformation/radarFrequency').text)
            radar_lambda = c/radar_freq

            metadata[filename]['Wavelength'] = radar_lambda

            metadata[filename]['Orbit'] = parseSatelliteData(satellite_filepath)


            # Currently a bug when reading in data using Sentinel-1 Driver
            # Directly reading the tif file to avoid issues

            # data_dict[filename] = dataset.ReadAsArray()
            data_dict[filename] = gdal.Open(dataset.GetFileList()[2]).ReadAsArray()

        return ImageWrapper(data_dict, meta_data=metadata)
