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
from skdaccess.utilities.grace_util import read_grace_data

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

        @param ap_paramList[geo_pont]: AutoList of geographic location tuples (lat,lon)
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


        csr_data = read_grace_data(os.path.join(data_location, csr_filename), 'lat','lon','lwe_thickness','time')
        jpl_data = read_grace_data(os.path.join(data_location, jpl_filename), 'lat','lon','lwe_thickness','time')
        gfz_data = read_grace_data(os.path.join(data_location, gfz_filename), 'lat','lon','lwe_thickness','time')

        
        scale_factor = read_grace_data(os.path.join(data_location, scale_factor_filename), 'Latitude', 'Longitude', 'SCALE_FACTOR')
        leakage_error = read_grace_data(os.path.join(data_location, scale_factor_filename), 'Latitude', 'Longitude', 'LEAKAGE_ERROR')
        measurement_error = read_grace_data(os.path.join(data_location, scale_factor_filename), 'Latitude', 'Longitude', 'MEASUREMENT_ERROR')        
            
        geo_point_list = self.ap_paramList[0]()

        # Get appropriate time range
        start_date = self.start_date
        end_date = self.end_date

        if start_date == None:
            start_date = np.min([csr_data.items[0], jpl_data.items[0], gfz_data.items[0]])


        if end_date == None:
            end_date = np.max([csr_data.items[-1], jpl_data.items[-1], gfz_data.items[-1]])

        data_dict = OrderedDict()
        metadata_dict = OrderedDict()
        for geo_point in geo_point_list:

            lat = geo_point[0]
            lon = (geo_point[1] + 360) % 360

            lat_index = floor(lat) + 0.5
            lon_index = floor(lon) + 0.5



            data = pd.DataFrame({'CSR' : csr_data.loc[start_date:end_date, lat_index, lon_index].copy(),
                                 'JPL' : jpl_data.loc[start_date:end_date, lat_index, lon_index].copy(),
                                 'GFZ' : gfz_data.loc[start_date:end_date, lat_index, lon_index].copy()})
            data.index.name = 'Date'


            label = str(geo_point[0]) + ', ' + str(geo_point[1])
            
            metadata_dict[label] = pd.Series({'scale_factor' : scale_factor.loc[lat_index, lon_index],
                                             'measurement_error' : measurement_error.loc[lat_index,lon_index],
                                             'leakage_error' : leakage_error.loc[lat_index, lon_index]})

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
                         
