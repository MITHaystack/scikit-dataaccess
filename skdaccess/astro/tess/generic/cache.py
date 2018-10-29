# The MIT License (MIT)
# Copyright (c) 2018 Massachusetts Institute of Technology
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

# mithagi required Base,Utils imports
from skdaccess.framework.data_class import DataFetcherCache, TableWrapper
from skdaccess.utilities.tess_utils import parseTessData

# Standard library imports
from collections import OrderedDict

# Third pary imports
from astropy.io import fits
from astropy.table import Table
import pandas as pd
import numpy as np


class DataFetcher(DataFetcherCache):
    ''' Data Fetcher for TESS data alerts '''
    def __init__(self, ap_paramList, toi_information):
        '''
        Initialize TESS Data Fetcher

        @param ap_paramList[tess_ids]: List of TESS IDs to retrieve
        @param start_url: URL to prepend before the TESS ID
        @param end_url: URL to append after the TESS ID
        '''
        self.toi_information = toi_information
        super(DataFetcher, self).__init__(ap_paramList)


    def getTargetInformation():
        """
        Retrieve Target list
        """
    pass

    def generateURLFromTID(self, tid_list):
        """
        Generate URL from TID

        @param tid: Input Tess ID
        @param return url to access data
        """
        pass

    def output(self):
        """
        Retrieve Tess data

        @return TableWrapper containing TESS lightcurves
        """
        tid_series = pd.Series([int(tid) for tid in self.ap_paramList[0]()])
        tid_string_list = [str(tid).zfill(16) for tid in tid_series]

        tid_not_found = tid_series.isin(self.toi_information['tic_id'])

        if np.count_nonzero(~tid_not_found) > 0:
            raise RuntimeError("No data for TID: " + str(tid_series[~tid_not_found].tolist()))

        url_list = self.generateURLFromTID(tid_string_list)

        file_list = self.cacheData('tess', url_list)

        data_dict = OrderedDict()
        metadata_dict = OrderedDict()

        for filename, tid in zip(file_list, tid_string_list):
            fits_data = fits.open(filename)
            data_dict[tid], metadata_dict[tid] = parseTessData(fits_data)


        return TableWrapper(data_dict, meta_data = metadata_dict)
