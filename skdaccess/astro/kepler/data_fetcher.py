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

# """@package Kepler
# Provides classes for accessing Kepler data.
# """

# mithagi required Base,Utils imports
from skdaccess.framework.data_class import DataFetcherCache, TableWrapper
from skdaccess.utilities.file_util import openPandasHDFStoreLocking

# Standard library imports
import re
import glob
import os
from collections import OrderedDict
from ftplib import FTP
from io import BytesIO
from tarfile import TarFile

# 3rd party package imports
import pandas as pd
import numpy as np
from astropy.table import Table
from astropy.io import fits



class DataFetcher(DataFetcherCache):
    ''' Data Fetcher for Kepler light curve data '''
    def __init__(self, ap_paramList, quarter_list=None):
        '''
        Initialize Kepler Data Fetcher

        @param ap_paramList[kepler_id_list]:  List of kepler id's
        @param quarter_list: List of quarters (0-17) (default: all quarters)
        '''

        self.quarter_list = quarter_list
        super(DataFetcher, self).__init__(ap_paramList)

    def _getKeplerFilePath(self):
        '''
        Get the path to the Kepler HDF file

        This helper function is for backwards compatibility as data
        locations for cached data are now all directories.

        @return String containing the path to the Kepler HDF file
        '''

        data_location = DataFetcher.getDataLocation('kepler')

        if os.path.split(data_location)[1] == 'kepler_data.h5':
            data_file_name = data_location
        else:
            data_file_name = os.path.join(data_location, 'kepler_data.h5')

        data_file_directory = os.path.split(data_file_name)[0]

        if not os.path.isdir(data_file_directory):
            os.makedirs(data_file_directory, exist_ok=True)

        return data_file_name

    def downloadKeplerData(self, kid_list):
        '''
        Download and parse Kepler data for a list of kepler id's

        @param kid_list: List of Kepler ID's to download

        @return dictionary of kepler data
        '''

        return_data = dict()

        # connect to ftp server
        ftp = FTP('archive.stsci.edu')
        ftp.login()

        # For each kepler id, download the appropriate data
        for kid in kid_list:
            ftp.cwd('/pub/kepler/lightcurves/' + kid[0:4] + '/' + kid)
            file_list = ftp.nlst()
            filename = None
            for file in file_list:
                match = re.match('kplr' + kid + '_lc_.*',file)
                if match:
                    filename = match.group(0)
                    break

            bio = BytesIO()
            ftp.retrbinary('RETR ' + filename, bio.write)
            bio.seek(0)

            # Read tar file
            tfile = tfile = TarFile(fileobj=bio)
            member_list = [member for member in tfile.getmembers()]

            # Extract data from tar file
            data_list = []
            for member in member_list:
                file = tfile.extractfile(member)
                fits_data = fits.open(file)
                data = Table(fits_data[1].data).to_pandas()
                data.set_index('CADENCENO',inplace=True)
                data.loc[:,'QUARTER'] = fits_data[0].header['QUARTER']
                data_list.append(data)
            full_data = pd.concat(data_list)
            return_data[kid] = full_data

        try:
            ftp.quit()
        except:
            ftp.close()

        return return_data
        
    def cacheData(self, data_specification):
        '''
        Cache Kepler data locally

        @param data_specification: List of kepler IDs
        '''

        kid_list = data_specification

        data_location = self._getKeplerFilePath()


        store = openPandasHDFStoreLocking(data_location, 'a')
        
        missing_kid_list = []
        for kid in kid_list:
            if 'kid_' + kid not in store:
                missing_kid_list.append(kid)

        
        if len(missing_kid_list) > 0:
            print("Downloading data for " + str(len(missing_kid_list)) + " star(s)")
            missing_kid_data = self.downloadKeplerData(missing_kid_list)

            for kid,data in missing_kid_data.items():
                store.put('kid_' + kid, data)

        store.close()

    def output(self):
        ''' 
        Output kepler data wrapper

        @return DataWrapper
        '''
        kid_list = self.ap_paramList[0]()
        kid_list = [ str(kid).zfill(9) for kid in kid_list ]

        self.cacheData(kid_list)

        data_location = self._getKeplerFilePath()

        kid_data = dict()

        store = openPandasHDFStoreLocking(data_location, 'r')

        for kid in kid_list:
            kid_data[kid] = store['kid_' + kid]
            # If downloaded using old skdaccess version
            # switch index
            if kid_data[kid].index.name == 'TIME':
                kid_data[kid]['TIME'] = kid_data[kid].index
                kid_data[kid].set_index('CADENCENO', inplace=True)


        store.close()                
        kid_data = OrderedDict(sorted(kid_data.items(), key=lambda t: t[0]))

        # If a list of quarters is specified, only select data in those quarters
        if self.quarter_list != None:        
            for kid in kid_list:
                kid_data[kid] = kid_data[kid][kid_data[kid]['QUARTER'].isin(self.quarter_list)]


        return TableWrapper(kid_data, default_columns = ['PDCSAP_FLUX'], default_error_columns = ['PDCSAP_FLUX_ERR'])
