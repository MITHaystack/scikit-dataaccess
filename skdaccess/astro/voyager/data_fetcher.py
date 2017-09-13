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


# Standard library imports
from collections import OrderedDict
import re

# 3rd part imports
import pandas as pd

class DataFetcher(DataFetcherCache):
    '''
    Data Fetcher for Mahali temperature data
    '''

    def __init__(self, start_year, end_year, spacecraft='both'):
        '''
        Initialize Voyager data fetcher

        @param start_year: Starting year
        @param end_year: Ending year
        @param spacecraft: Which spaceraft to use (voyager1, voyager2, or both).
        '''

        # Generate list of years for retrieving data
        self.year_list = list(range(start_year, end_year+1))

        # Create a list of spacecraft data to download
        if spacecraft not in ('voyager1', 'voyager2', 'both'):
            raise RuntimeError('Spacecraft not understood')

        if spacecraft == 'both':
            self.spacecraft_list = ['voyager1', 'voyager2']
        else:
            self.spacecraft_list = [spacecraft]



        # Field names for parsing data
        self.field_names = [
            'Year', 'Day', 'Hour', 'Distance', 'Latitude', 'Longitude',
            'Field_Magnitude_Average', 'Magnitude_of_Average_Field', 'BR', 'BT',
            'BN', 'Flow_Speed', 'Theta', 'Phi', 'Proton_Density',
            'Proton_Temperature', 'LECP_1', 'LECP_2', 'LECP_3', 'CRS_1', 'CRS_2',
            'CRS_3', 'CRS_4', 'CRS_5', 'CRS_6', 'CRS_7', 'CRS_8', 'CRS_9',
            'CRS_10', 'CRS_11', 'CRS_12', 'CRS_13', 'CRS_14', 'CRS_15', 'CRS_16',
            'CRS_17', 'CRS_18',
        ]


        # Field widths as the data is fixed width format
        self.field_widths = [
            4, 4, 3, 7, 7, 7, 8, 8, 8, 8, 8, 7, 7, 7, 9, 9,
            10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10,
            10, 10, 10, 10, 10, 10, 10, 10, 10
        ]

        # Base data location url
        self.base_url = 'https://spdf.gsfc.nasa.gov/pub/data/voyager/'


        super(DataFetcher, self).__init__([])

    def generateURL(self, spacecraft, in_year):
        '''
        Generate url for voyager data

        @param spacecraft: Voyager spacecraft (vy1 or vy2)
        @param in_year: Input year (or 'metadata')

        @return Url of data location
        '''

        num = spacecraft[-1]

        url = self.base_url + 'voyager' + num + '/merged/'

        if in_year == 'metadata':
            url = url + 'vy' + num + 'mgd.txt'

        else:
            url = url + 'vy' + num + '_' + str(in_year) + '.asc'

        return url


    def parseVoyagerData(self, spacecraft, in_filename):
        '''
        Parse Voyager Data

        @param spacecraft: Voyager spacecraft (vy1 or vy2)
        @param in_filename: Input voyager data filename

        @return Pandas Dataframe of Voyager data
        '''

        def convert_date(year, day, hour):
            '''
            Convert to datetime

            @param year: Input year
            @param day: Input day
            @param hour: Input hour

            @return datetime
            '''

            return pd.to_datetime("{0:0>4}{1:0>3}{2:0>2}".format(year,day,hour), format='%Y%j%H')


        # Voyager 1 has 3 less columns than Voyager 2
        if spacecraft == 'voyager1':
            field_widths = self.field_widths[:34]
            field_names = self.field_names[:34]
        else:
            field_widths = self.field_widths
            field_names = self.field_names

        # Parse the data
        data = pd.read_fwf(in_filename, widths=field_widths, header=None, names=field_names)

        # Create date column
        data['Date'] = list(map(convert_date,
                                data.loc[:,'Year'],
                                data.loc[:,'Day'],
                                data.loc[:,'Hour']))

        data.set_index('Date', inplace=True)

        return data


    def parseVoyagerMetadata(self, in_file):
        ''' Parse voyager metadata

        @param in_file: Input filename

        @return Dictionary containing metadata
        '''
        with open(in_file,'r',errors='ignore') as metafile:
            lines = metafile.readlines()
            lines = [line.rstrip() for line in lines]

        start_index = -1
        end_index = -1
        prev_line = None
        for index, line in enumerate(lines):
            if re.search('FORMAT DESCRIPTION',line):
                start_index = index+4

            if prev_line == '' and line == '' and start_index > -1:
                end_index = index - 2
                break

            prev_line = line

        description_data = lines[start_index:end_index+1]


        field_index = 0
        description_dict = OrderedDict()

        for line in description_data:

            if re.search('\s+[0-9]+', line[:6]):
                info = re.split('\s\s+',line)[1:]
                key = self.field_names[field_index]
                description_dict[key] = OrderedDict()
                description_dict[key]['MEANING'] = info[2]
                description_dict[key]['UNITS/COMMENTS'] = info[3]
                field_index += 1

            elif line.strip() != '':
                description_dict[key]['MEANING'] = description_dict[key]['MEANING'] + ' ' + line.strip()

        return description_dict


    def getMetadataFiles(self):
        '''
        Get path to metadata file

        Metadata will download if necessary

        @return List containing file path(s) for the metadata
        '''

        urls = [self.generateURL(spacecraft, 'metadata') for spacecraft in self.spacecraft_list]

        return self.cacheData('voyager', urls)

    def output(self):
        '''
        Generate data wrapper

        @return data wrapper of voyager data
        '''

        # Generate url_list
        url_list = []
        for spacecraft in self.spacecraft_list:
            url_list += [self.generateURL(spacecraft, 'metadata')]
            url_list += [self.generateURL(spacecraft, year) for year in self.year_list]

        full_filenames = self.cacheData('voyager', url_list)
        num_files = len(self.year_list) + 1

        # Parse downloaded data
        data_dict = OrderedDict()
        metadata_dict = OrderedDict()
        for index, spacecraft in enumerate(self.spacecraft_list):
            # Need to select data for this spacecraft
            filenames = full_filenames[num_files * index : num_files * (1+index)]

            # parse data
            metadata_dict[spacecraft] = self.parseVoyagerMetadata(filenames[0])
            data_list = [self.parseVoyagerData(spacecraft, filename) for filename in filenames[1:]]
            data_dict[spacecraft] = pd.concat(data_list)

        return TableWrapper(data_dict, meta_data = metadata_dict, default_columns = ['BR','BT','BN'])

