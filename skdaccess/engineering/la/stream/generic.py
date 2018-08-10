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
import json

# Scikit Data Access imports
from skdaccess.framework.data_class import DataFetcherStream, TableWrapper

# Third party imports
from six.moves.urllib.parse import urlencode
from six.moves.urllib.request import urlopen
import pandas as pd

class DataFetcher(DataFetcherStream):
    """
    Class for handling data requests to data.lacity.org
    """
    
    def __init__(self, endpoint, parameters, label, verbose=False, app_token = None):
        """
        Initialize Data Fetcher for accessing data.lacity.org

        @param endpoint: Data endpoint string
        @param parameters: Parameters to use when retrieving dta
        @param label: Label of pandas dataframe
        @param verbose: Print out extra information
        @param app_token: Application token to use to avoid throttling issues
        """
        self.base_url = 'https://data.lacity.org/resource/'
        self.base_url_and_endpoint = self.base_url + endpoint + '.json?'
        
        self.parameters = parameters        
        self.label = label        
        self.app_token = app_token

        if '$$app_token' in parameters:
            raise RuntimeError("Use app_token option in constructor instead of manually " + 
                               "adding it into the the parameters")

        if app_token != None:
            self.parameters['$$app_token'] = app_token
            
        super(DataFetcher, self).__init__([], verbose)

    def output(self):
        """
        Retrieve data from data.lacity.org

        @return Table wrapper of containing specified data
        """
        data_dict = OrderedDict()
        url_query = self.base_url_and_endpoint + urlencode(self.parameters)

        with urlopen(url_query) as remote_resource:
            decoded_json = json.loads(remote_resource.read().decode())

        data_dict[self.label] = pd.DataFrame.from_dict(decoded_json)

        return TableWrapper(data_dict)
        
