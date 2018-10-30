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

# Skdaccess imports
from skdaccess.astro.tess.generic.cache import DataFetcher as GenericDF
from skdaccess.framework.data_class import DataFetcherCache

# 3rd party imports
import pandas as pd


class DataFetcher(GenericDF):
    ''' Data Fetcher for TESS data alerts '''
    def __init__(self, ap_paramList):
        '''
        Initialize TESS Data Fetcher

        @param ap_paramList[tess_ids]: List of TESS IDs to retrieve
        @param start_url: URL to prepend before the TESS ID
        @param end_url: URL to append after the TESS ID
        '''
        toi_information = DataFetcher.getTargetInformation()

        self.start_url = 'https://archive.stsci.edu/missions/tess/ete-6/tid/'
        self.end_url = '-0016-s_lc.fits'

        super(DataFetcher, self).__init__(ap_paramList, toi_information)

    def generateURLFromTID(self, tid_list):
        """
        Generate URL from TID

        @param tid_list: Input Tess ID list
        @param return url to access data
        """

        url_list = []
        for tid in tid_list:
            url_path =   tid[:2] + '/' \
                       + tid[2:5] + '/' \
                       + tid[5:8] + '/' \
                       + tid[8:11] + '/'

            url_list.append(self.start_url + url_path + 'tess2019128220341-' + tid + self.end_url)

        return url_list


    def getTargetInformation():
        """
        Retrieve Target information for TESS data alerts
        """

        toi_url = 'https://archive.stsci.edu/missions/tess/ete-6/tid/tess2018072154700_toi.csv'

        df_cache = DataFetcherCache()

        return pd.read_csv(df_cache.cacheData('tess', [toi_url], use_progress_bar=False)[0]).rename(columns={'# planets' : 'planets'})
