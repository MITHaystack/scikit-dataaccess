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
from skdaccess.framework.data_class import DataFetcherCache, XArrayWrapper
from skdaccess.utilities.sounding_util import SoundingParser, generateQueries, convertToStr


# 3rd party imports
import pandas as pd
import numpy as np
import xarray as xr
import pygrib

# Standard library imports
from collections import OrderedDict
from http.cookiejar import LWPCookieJar
import os
from urllib.parse import urlencode
from urllib.request import HTTPCookieProcessor, build_opener
from datetime import datetime


def _extractParamters(data_list, data_names, levels):
    '''
    Extract data from grib2 era-I data

    Written for ERA Interim atmospheric model analysis interpolated to pressure levels

    @param data_list: List of opened files in pygrib
    @param data_names: Names of data to pull from pygrib files
    @param levels: Number of levels of data
    '''
    # This list contains redundant data
    skip_list = ['latLonValues', 'distinctLatitudes','distinctLongitudes',
                 'values', 'longitudes','latitudes', 'level', 'year',
                 'month','day','hour','minute','second']

    # These records can change every level and date
    multi_level_records = ['referenceValue', 'maximum', 'minimum','average',
                           'standardDeviation', 'skewness', 'kurtosis',
                           'binaryScaleFactor', 'packingError', 'unpackedError',
                           'referenceValueError']

    # These records can change every date, but not every level
    multi_date_records = ['yearOfCentury','dataDate', 'validityTime',
                          'julianDay', 'validityDate', 'dataTime']


    class MetadataMismatch(Exception):
        ''' Raised if Metadata from different levels doesn't match '''


    lat = None
    lon = None

    data_dict = OrderedDict()
    meta_dict = OrderedDict()

    data_time_list = []
    date_range = []

    meta_time_dict = OrderedDict()
    meta_only_time_dict = OrderedDict()

    # Loop over every data file
    for weather in data_list:

        weather.rewind()

        # Need to determine the date of each file once
        measured_date = False

        # Loop over every requested data product
        for data_name in data_names:

            # If no meta data exists yet, add it
            if data_name not in meta_dict:
                meta_dict[data_name] = OrderedDict()


            # List to hold data
            data_list = []
            prev_level = None

            meta_multi_dict = OrderedDict()
            meta_only_time_temp_dict = OrderedDict()

            for index, record in enumerate(weather.select(name=data_name)):
                # Need to record latitude and longitude the first time through
                if lat is None:
                    lat, lon =  record.latlons()

                # If date hasn't been recorded yet, save it
                if measured_date == False:
                    date = datetime(record['year'], record['month'], record['day'],
                                    record['hour'], record['minute'], record['second'])

                    date_range.append(pd.to_datetime(date))
                    measured_date = True

                # If the data is iterated through out of order
                # throw an exception
                if record['level'] != levels[index]:
                    raise RuntimeError('Level mismatch')

                # loop over key in the record
                for label in record.keys():
                    if label not in skip_list:
                        try:
                            # This covers if the record can change
                            # each level/date
                            if label in multi_level_records:

                                if label not in meta_multi_dict:
                                    meta_multi_dict[label] = []

                                meta_multi_dict[label].append(record[label])

                            # This covers metadata that changes in time but no in levels
                            elif label in multi_date_records:
                                if label not in meta_only_time_temp_dict:
                                    meta_only_time_temp_dict[label] = OrderedDict()
                                    meta_only_time_temp_dict[label]['index'] = date_range[-1]
                                    meta_only_time_temp_dict[label]['data'] = record[label]
                                else:
                                    if meta_only_time_temp_dict[label]['index'] != date_range[-1] or \
                                       meta_only_time_temp_dict[label]['data'] != record[label]:
                                        raise MetadataMismatch


                            # If the metadata doesn't exist yet, add it to the metadata dictionary
                            elif label not in meta_dict[data_name]:
                                meta_dict[data_name][label] = record[label]

                            # If the metadata already exists, check to make sure it
                            # hasn't changed
                            elif np.all(meta_dict[data_name][label] != record[label]):
                                print(label, meta_dict[data_name][label], record[label])
                                raise MetadataMismatch('Levels have different metadata')

                        # Sometimes there is not value for a key. A runtime exception is thrown
                        # in this case
                        except RuntimeError as RE:
                            if label not in meta_dict[data_name] or meta_dict[data_name][label] == None:
                                meta_dict[data_name][label] = None
                            else:
                                raise MetadataMismatch('Levels have different metadata')

                # Record the data for this level
                data_list.append(record['values'])

            # If data hasn't been added to the dictionary yet, add it
            if data_name not in data_dict:
                data_dict[data_name] = []

            # Create a stack from each level
            data_dict[data_name].append(np.stack(data_list))

            # Need to save metadata that changes each level/date
            for label, data in meta_multi_dict.items():

                # Check that it has the correct number of data points
                if len(data) != len(levels):
                    raise RuntimeError('Missing metadata')

                # If no key is in meta_time_dict for the data, add it
                # This dictionary stores metadata that changes with
                # levels / time
                if data_name not in meta_time_dict:
                    meta_time_dict[data_name] = OrderedDict()

                # If this particular metadata hasn't been saved before,
                # add an entry for it
                if label not in meta_time_dict[data_name]:
                    meta_time_dict[data_name][label] = OrderedDict()

                # Finally, add the metadata as a pandas series to the metadata
                meta_time_dict[data_name][label][date_range[-1]] = pd.Series(data,index=levels)
                meta_time_dict[data_name][label][date_range[-1]].index.name = 'Level'

            # Need to save metadata that changes for date only
            for label, data in meta_only_time_temp_dict.items():
                if data_name not in meta_only_time_dict:
                    meta_only_time_dict[data_name] = OrderedDict()

                if label not in meta_only_time_dict[data_name]:
                    meta_only_time_dict[data_name][label] = OrderedDict()
                    meta_only_time_dict[data_name][label]['index']  = []
                    meta_only_time_dict[data_name][label]['data'] = []

                meta_only_time_dict[data_name][label]['index'].append(data['index'])
                meta_only_time_dict[data_name][label]['data'].append(data['data'])



    # Convert sequence of data cubes to a 4d array
    for label in data_dict.keys():
        data_dict[label] = (['time','z','y','x'], np.stack(data_dict[label]))

    # Create dataframes for metadata that changes in levels and time
    for data_name, labels in meta_time_dict.items():
        for label, dates in labels.items():
            meta_dict[data_name][label] = pd.DataFrame.from_dict(dates)

    # Create pandas series for metadata that changes in time
    for data_name, labels in meta_only_time_dict.items():
        for label, data in labels.items():
            meta_dict[data_name][label] = pd.Series(data['data'], index=data['index'])
            meta_dict[data_name][label].index.name = 'Date'


    # Create dataset
    ds = xr.Dataset(data_dict, coords={'lat': (['y','x'], lat),
                                       'lon': (['y','x'], lon),
                                       'pressure': (['z'], levels),
                                       'time': date_range})

    # Set metadata
    for label, metadata in meta_dict.items():
        ds[label].attrs = metadata


    return ds

class DataFetcher(DataFetcherCache):
    ''' DataFetcher for retrieving ERA-I data '''
    def __init__(self, date_list, data_names, username, password):
        '''
        Initialize Data Fetcher

        @param date_list: list of dates
        @param data_names: list of data names
        @param username: UCAR username
        @param password: UCAR password
        '''

        self.date_list = date_list
        self.data_names = data_names
        self.username = username
        self.password = password


        super(DataFetcher, self).__init__()

    def output(self):
        '''
        Generate data wrapper

        @return Era-I weather in a data wrapper
        '''


        class ExpiredCookieError(Exception):
            ''' Exception to use if cookie is expired '''

        class IncorrectNumberOfCookies(Exception):
            ''' Exception to use if the number of cookies loaded is incorrect '''


        def getCookies(cookies):
            request = OrderedDict()
            request['email'] = self.username
            request['passwd'] = self.password
            request['action'] = 'login'

            data = urlencode(request).encode()

            url_opener = build_opener(HTTPCookieProcessor(cookies))

            with url_opener.open('https://rda.ucar.edu/cgi-bin/login', data) as myurl:
                cookies.save()

        # Get absolute path to data directory
        data_location = DataFetcherCache.getDataLocation('era_interim')

        # Create cookiejar
        cookiejar = LWPCookieJar(os.path.join(data_location, 'cookies.txt'))

        try:
            cookiejar.load()

            if len(cookiejar) != 3:
                raise IncorrectNumberOfCookies

            current_time = pd.to_datetime(pd.datetime.utcnow())

            for cookie in cookiejar:
                expiration_time = pd.to_datetime(cookie.expires, unit='s')

                # If cookie has less than a week left, recreate all cookies
                if (expiration_time - current_time) < pd.to_timedelta('7D'):
                    raise ExpiredCookieError

        # No cookie file
        except (FileNotFoundError, IncorrectNumberOfCookies):
            cookiejar.clear()
            getCookies(cookiejar)

        # Cookies will expire soon or have already expired
        except ExpiredCookieError:
            cookiejar.clear()
            getCookies(cookiejar)


        base_url = 'https://rda.ucar.edu/data/ds627.0/ei.oper.an.pl/'

        url_list = [ date.strftime('%Y%m/ei.oper.an.pl.regn128sc.%Y%m%d%H')
                     for date in self.date_list ]

        url_list = [ base_url + url for url in url_list ]

        file_list = self.cacheData('era_interim', url_list, cookiejar=cookiejar)

        pygrib_files = [pygrib.open(filename) for filename in file_list]

        levels = [
            1,    2,    3,    5,    7,   10,   20,   30,   50,   70,  100,
            125,  150,  175,  200,  225,  250,  300,  350,  400,  450,  500,
            550,  600,  650,  700,  750,  775,  800,  825,  850,  875,  900,
            925,  950,  975, 1000
        ]

        data = _extractParamters(pygrib_files, self.data_names, levels)

        wrapped_data = XArrayWrapper(data, self.data_names)

        return wrapped_data
