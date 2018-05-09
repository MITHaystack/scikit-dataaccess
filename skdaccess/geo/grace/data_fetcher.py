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

# """@package GRACE
# Provides classes for accessing GRACE data.
# """

# mithagi required Base imports
from skdaccess.framework.data_class import DataFetcherStorage, TableWrapper
from skdaccess.utilities.grace_util import readTellusData, getStartEndDate

# standard library imports
import re
from ftplib import FTP
import os
import glob
from collections import OrderedDict
from configparser import NoSectionError, NoOptionError
from glob import glob
from math import floor

# 3rd party package imports
import pandas as pd
import numpy as np
from tqdm import tqdm


class DataFetcher(DataFetcherStorage):
    ''' Data Fetcher for GRACE data '''

    def __init__(self, ap_paramList, start_date = None, end_date = None):
        '''
        Construct a Grace Data Fetcher

        @param ap_paramList[geo_point]: AutoList of geographic location tuples (lat,lon)
        @param start_date: Beginning date
        @param end_date: Ending date
        '''
        
        self.start_date = start_date
        self.end_date = end_date
        super(DataFetcher, self).__init__(ap_paramList)
        
    def output(self):
        ''' 
        Create data wrapper of grace data for specified geopoints.

        @return Grace Data Wrapper
        '''

        conf = DataFetcher.getConfig()

        try:
            data_location = conf.get('grace', 'data_location')
            csr_filename = conf.get('grace', 'csr_filename')
            jpl_filename = conf.get('grace', 'jpl_filename')
            gfz_filename = conf.get('grace', 'gfz_filename')
            scale_factor_filename = conf.get('grace', 'scale_factor_filename')


        except (NoOptionError, NoSectionError) as exc:
            print('No data information available, please run: skdaccess grace')
            raise exc

        geo_point_list = self.ap_paramList[0]()

        csr_data, csr_meta, lat_bounds, lon_bounds = readTellusData(os.path.join(data_location, csr_filename), geo_point_list, 'lat','lon',
                                                                    'lwe_thickness', 'CSR','time')
        jpl_data, jpl_meta, = readTellusData(os.path.join(data_location, jpl_filename), geo_point_list, 'lat','lon',
                                             'lwe_thickness', 'JPL','time', lat_bounds=lat_bounds, lon_bounds=lon_bounds)[:2]
        gfz_data, gfz_meta, = readTellusData(os.path.join(data_location, gfz_filename), geo_point_list, 'lat','lon',
                                             'lwe_thickness', 'GFZ','time', lat_bounds=lat_bounds, lon_bounds=lon_bounds)[:2]

        
        scale_factor_data, scale_factor_meta, = readTellusData(os.path.join(data_location, scale_factor_filename),
                                                               geo_point_list, 'Latitude', 'Longitude', 'SCALE_FACTOR',
                                                               lat_bounds=lat_bounds, lon_bounds=lon_bounds)[:2]
        leakage_error_data, leakage_error_meta, = readTellusData(os.path.join(data_location, scale_factor_filename),
                                                                 geo_point_list, 'Latitude', 'Longitude', 'LEAKAGE_ERROR',
                                                                 lat_bounds=lat_bounds, lon_bounds=lon_bounds)[:2]
        measurement_error_data, measurement_error_meta, = readTellusData(os.path.join(data_location, scale_factor_filename),
                                                                         geo_point_list, 'Latitude', 'Longitude',
                                                                         'MEASUREMENT_ERROR', lat_bounds=lat_bounds,
                                                                         lon_bounds=lon_bounds)[:2]
        # Get appropriate time range
        start_date = self.start_date
        end_date = self.end_date


        def getMaskedValue(in_value):
            '''
            Retrieve the value if not masked,
            otherwise return np.nan

            @param in_value: Input value to check

            @return input value or nan
            '''
            if np.ma.is_masked(in_value):
                return np.nan
            else:
                return in_value



        if start_date == None or end_date == None:
            csr_start_date, csr_end_date = getStartEndDate(csr_data)
            jpl_start_date, jpl_end_date = getStartEndDate(jpl_data)
            gfz_start_date, gfz_end_date = getStartEndDate(gfz_data)


        if start_date == None:
            start_date = np.min([csr_start_date, jpl_start_date, gfz_start_date])


        if end_date == None:
            end_date = np.max([csr_end_date, jpl_end_date, gfz_end_date])

        data_dict = OrderedDict()
        metadata_dict = OrderedDict()
        for (csr_label, csr_frame), (jpl_label, jpl_frame), (gfz_label, gfz_frame) in zip(csr_data.items(),
                                                                                          jpl_data.items(),
                                                                                          gfz_data.items()):


            data = pd.concat([csr_frame.loc[start_date:end_date],
                              jpl_frame.loc[start_date:end_date],
                              gfz_frame.loc[start_date:end_date]], axis=1)

            data.index.name = 'Date'


            label = csr_label
            
            metadata_dict[label] = pd.Series({'scale_factor' : getMaskedValue(scale_factor_data[csr_label]),
                                             'measurement_error' : getMaskedValue(measurement_error_data[csr_label]),
                                              'leakage_error' : getMaskedValue(leakage_error_data[csr_label])})

            data_dict[label] = data

        
        metadata_frame = pd.DataFrame.from_dict(metadata_dict)
        return(TableWrapper(data_dict,meta_data = metadata_frame,default_columns=['CSR','JPL','GFZ']))
            

    def __str__(self):
        '''
        String representation of data fetcher

        @return String listing the name and geopoint of data fetcher
        '''
        return 'Grace Data Fetcher' + super(DataFetcher, self).__str__()


    @classmethod
    def downloadFullDataset(cls, out_file = 'grace.h5', use_file = None):
        '''
        Download and parse data from the Gravity Recovery and Climate Experiment.

        @param out_file: Output filename for parsed data
        @param use_file: Directory of already downloaded data. If None, data will be downloaded.

        @return Absolute path of parsed data
        '''
        # Get date of grace data from filename

        def setConfigFile(filename):
            if re.search('SCALE_FACTOR', filename):
                DataFetcher.setDataLocation('grace', filename, key='scale_factor_filename')

            elif re.search('CSR', filename):
                DataFetcher.setDataLocation('grace', filename, key='csr_filename')

            elif re.search('GFZ', filename):
                DataFetcher.setDataLocation('grace', filename, key='gfz_filename')

            elif re.search('JPL', filename):
                DataFetcher.setDataLocation('grace', filename, key='jpl_filename')

            else:

                return False

            return True

        if use_file is None:
            print("Downloading GRACE Land Mass Data")
            ftp = FTP("podaac-ftp.jpl.nasa.gov")
            ftp.login()
            ftp.cwd('/allData/tellus/L3/land_mass/RL05/netcdf')
            dir_list = list(ftp.nlst(''))
            file_list = [file for file in dir_list if re.search('.nc$', file)]
            for filename in tqdm(file_list):

                status = setConfigFile(filename)

                if status == False:
                    print("Uknown file:", filename)
                    continue

                
                ftp.retrbinary('RETR ' + filename, open(filename, 'wb').write)
                
            ftp.quit()
            DataFetcher.setDataLocation('grace', os.path.abspath('./'))

        else:
            files = glob(os.path.join(use_file, '*.nc'))

            for filename in files:
                status = setConfigFile(filename)

            if status == False:
                print('Unknown file')

            DataFetcher.setDataLocation('grace', os.path.abspath(use_file))
                         
