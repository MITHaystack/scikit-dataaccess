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

# Standard library imports
from collections import OrderedDict

# Scikit Data Access
from skdaccess.engineering.la.generic.stream import DataFetcher as GenericDataFetcher
from skdaccess.utilities.support import join_string

# Third party packages
import pandas as pd

class DataFetcher(GenericDataFetcher):
    """
    DataFetcher for retrieving traffic counts from LA
    """
    def __init__(self, limit=None, start_time=None, end_time=None, app_token=None, verbose=False):
        """
        Initialize Data Fetcher to retrieve traffic couns from LA

        @param limit: Maximum number of rows
        @param start_time: Starting time
        @param end_time: Ending time
        @param app_token: Application token to avoid throttling
        @param verbose: Print extra information
        """
        
        endpoint = 'w4g9-ux6z'

        where_string = ''

        time_list = []

        if start_time != None:
            time_list.append((start_time, "count_date >= '{}'"))

        if end_time != None:
            time_list.append((end_time, "count_date <= '{}'"))
        
        for time, compare_string in time_list:
            time = pd.to_datetime(time)
            
            where_string = join_string(where_string,
                                       compare_string.format(time.strftime('%Y-%m-%dT%H:%M:%S')))

        parameters = OrderedDict()

        if len(time_list) > 0:
            parameters['$where'] = where_string

        if limit != None:
            parameters['$limit'] = str(limit)
            
        super(DataFetcher, self).__init__(endpoint = endpoint,
                                          parameters = parameters,
                                          label = 'Traffic Counts',
                                          app_token = app_token,
                                          verbose = verbose,
                                          header = 0,
                                          parse_dates = [0])
