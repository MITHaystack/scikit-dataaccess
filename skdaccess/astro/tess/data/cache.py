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
        '''

        self.start_url = 'https://archive.stsci.edu/hlsps/tess-data-alerts/hlsp_tess-data-alerts_tess_phot_'
        self.end_url = '-s01_tess_v1_lc.fits'
        toi_information = DataFetcher.getTargetInformation()

        super(DataFetcher, self).__init__(ap_paramList, toi_information)

    def generateURLFromTID(self, tid_list):
        """
        Generate URL from TID

        @param tid_list: List of input Tess IDs
        """
        return [ self.start_url + tid[-11:] + self.end_url for tid in tid_list]

    def getTargetInformation():
        """
        Retrieve Target information for TESS Data Alerts

        @return Pandas DataFrame of containing target information
        """

        toi_url = 'https://archive.stsci.edu/hlsps/tess-data-alerts/hlsp_tess-data-alerts_tess_phot_alert-summary-s01+s02_tess_v3_spoc.csv'

        df_cache = DataFetcherCache()

        return pd.read_csv(df_cache.cacheData('tess', [toi_url], use_progress_bar=False)[0], escapechar='#')
