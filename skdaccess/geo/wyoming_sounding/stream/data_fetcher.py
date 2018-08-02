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
from skdaccess.framework.data_class import DataFetcherStream, TableWrapper
from skdaccess.utilities.sounding_util import SoundingParser, generateQueries


# 3rd party imports
import pandas as pd
import numpy as np
from six.moves.urllib.request import urlopen

# Standard library imports
from collections import OrderedDict

class DataFetcher(DataFetcherStream):
    ''' DataFetcher for retrieving Wyoming Sounding data '''
    def __init__(self, station_number, year, month, day_start, day_end, start_hour = 0, end_hour = 12):
        '''
        Initialize Data Fetcher

        @param station_number: Station number
        @param year: Input year
        @param month: Input month (Integer for a single month, or a list of integers for multiple months)
        @param day_start: First day of the month to include
        @param day_end: Last day of the month to include
        @param start_hour: Starting hour (may be either 0 or 12)
        @param end_hour: Ending hour (may be either 0 or 12)
        '''

        self.station_number = station_number

        if np.isscalar(year):
            self.year_list = [year]
        else:
            self.year_list = year

        if np.isscalar(month):
            self.month_list = [month]
        else:
            self.month_list = month

        self.day_start = day_start
        self.day_end = day_end
        self.start_hour = start_hour
        self.end_hour = end_hour



        super(DataFetcher, self).__init__()

    def output(self, shared_lock = None, shared_list = None):
        '''
        Generate data wrapper

        @return Wyoming sounding data in a data wrapper
        '''

        full_results_dict = OrderedDict()
        full_meta_dict = OrderedDict()


        for query_url in generateQueries(self.station_number, self.year_list, self.month_list, self.day_start,
                                         self.day_end, self.start_hour, self.end_hour):

            with urlopen(query_url) as in_data:
                sp = SoundingParser()
                sp.feed(in_data.read().decode())

            for key, data in sp.data_dict.items():
                full_results_dict[key] = data

            for key, data in sp.metadata_dict.items():
                full_meta_dict[key] = data


        return TableWrapper(obj_wrap = full_results_dict, meta_data = full_meta_dict)
