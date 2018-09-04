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
from getpass import getpass

# Scikit Data Access
from skdaccess.framework.data_class import DataFetcherStream, TableWrapper

# Third party packages
import pandas as pd
from alpha_vantage.timeseries import TimeSeries

class DataFetcher(DataFetcherStream):

    """ Data Fetcher for retrieving stock data """

    def __init__(self, ap_paramList, data_type, start_date=None, end_date=None, interval=None):
        """
        @param ap_paramList[stock_symbol_list]: AutoList of stock symbols
        @param data_type: Type of data to retrieve (daily, daily_adjusted, intraday, monthly, monthly_adjusted, weekly, weekly_adjusted)
        @param start_date: Starting date
        @param end_date: Ending date
        @param interval: Interval for intraday (1min, 5min, 15min, 30min, 60min)
        @return: Table data wrapper of stock data
        """

        self.data_type = data_type
        self.start_date = start_date
        self.end_date = end_date
        self.interval = interval

        self.possible_intervals = ('1min', '5min', '15min', '30min', '60min')
        self.possible_data_types = ("daily", "daily_adjusted", "intraday", "monthly", "monthly_adjusted", "weekly", "weekly_adjusted")


        if interval not in self.possible_intervals and data_type == 'intraday':
            raise RuntimeError('Did not understand interval: "' + str(interval) +  '" to use with intraday data type')

        elif interval is not None and data_type != 'intraday':
            raise RuntimeError('interval is only used with data type intraday')

        api_key = DataFetcher.getConfigItem('stocks', 'api_key')
        write_key = False
        
        while api_key is None or api_key == "":
            api_key = getpass(prompt='Alpha Vantage API key')
            write_key = True

        if write_key:
            DataFetcher.writeConfigItem('stocks','api_key', api_key)

        super(DataFetcher, self).__init__(ap_paramList)

    def output(self):
        """
        Retrieve stock data
        
        @return TableWrapper of stock data
        """

        stock_symbols = self.ap_paramList[0]()

        timeseries_retriever = TimeSeries(key=DataFetcher.getConfigItem('stocks','api_key'),
                                          output_format='pandas',
                                          indexing_type = 'date')

        data_dict = OrderedDict()
        metadata_dict = OrderedDict()

        for symbol in stock_symbols:

            # Extract data
            if self.data_type == 'daily':
                data, metadata = timeseries_retriever.get_daily(symbol, outputsize='full')
            elif self.data_type == 'daily_adjusted':
                data, metadata = timeseries_retriever.get_daily_adjusted(symbol, outputsize='full')
            elif self.data_type == 'monthly':
                data, metadata = timeseries_retriever.get_monthly(symbol)
            elif self.data_type == 'monthly_adjusted':
                data, metadata = timeseries_retriever.get_monthly_adjusted(symbol)
            elif self.data_type == 'weekly':
                data, metadata = timeseries_retriever.get_weekly(symbol)
            elif self.data_type == 'weekly_adjusted':
                data, metadata = timeseries_retriever.get_weekly_adjusted(symbol)
            elif self.data_type == 'intraday':
                data, metadata = timeseries_retriever.get_weekly_adjusted(symbol, self.interval, outputsize='full')
            # Convert index to pandas datetime
            if self.data_type == 'intraday':
                data.index = pd.to_datetime(data.index).tz_localize(metadata['6. Time Zone'])
            else:
                data.index = pd.to_datetime(data.index)


            data_dict[symbol] = data[self.start_date:self.end_date]
            metadata_dict[symbol] = metadata

        return TableWrapper(data_dict, meta_data = metadata_dict)
