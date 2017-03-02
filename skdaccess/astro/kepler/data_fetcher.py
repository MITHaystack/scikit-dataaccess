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

"""@package Kepler
Provides classes for accessing Kepler data.
"""

# mithagi required Base,Utils imports
from skdaccess.framework.data_class import DataFetcherBase, DictionaryWrapper
from skdaccess.utilities import trend_util
from skdaccess.astro.kepler.data_wrapper import DataWrapper
from skdaccess.utilities import data_util

# Standard library imports
from collections import OrderedDict
import re
import glob
import os

# 3rd party package imports
import pandas as pd
import numpy as np
from astropy.table import Table
from astropy.io import fits


class DataFetcher(DataFetcherBase):
    ''' Data Fetcher for Kepler light curve data '''
    def __init__(self, ap_paramList, normalize=False, drop_on_quality=False, filter_window=None, quarter_list=None, wrapper_type = 'series'):
        '''
        Initialize Kepler Data Fetcher

        @param ap_paramList[kepler_id_list]:  List of kepler id's
        @param normalize: Normalize the PDCSAP_FLUX
        @param drop_on_quality: Drop data if SAP_QUALITY != 0 
        @param filter_window: Size of window used when removing systematic offsets.
        @param quarter_list: List of quarters (0-17)
        @param wrapper_type: Select the type of iterator wrapper to generate, as series or table
        '''

        self.normalize = normalize
        self.drop_on_quality = drop_on_quality
        self.filter_window = filter_window
        self.quarter_list = quarter_list
        self.wrapper_type = wrapper_type
        super(DataFetcher, self).__init__(ap_paramList)
        
    def output(self):
        ''' 
        Output kepler data wrapper

        @return DataWrapper
        '''

        data_location = data_util.getDataLocation('kepler', raise_exception = False)

        if data_location == None:
            data_location = os.path.join(os.path.expanduser('~'), '.skdaccess', 'kepler')
            os.makedirs(data_location, exist_ok=True)
            data_location = os.path.join(data_location, 'kepler_data.h5')
            data_util.setDataLocation('kepler', data_location)

        store = pd.HDFStore(data_location)

        kid_list = self.ap_paramList[0]()
        kid_list = [ str(kid).zfill(9) for kid in kid_list ]
        missing_kid_list = []
        kid_data = dict()
        for kid in kid_list:
            try:
                kid_data[kid] = store['kid_' + kid]
            except:
                missing_kid_list.append(kid)

        if len(missing_kid_list) > 0:
            print("Downloading data for " + str(len(missing_kid_list)) + " star(s)")
            missing_kid_data = data_util.downloadKeplerData(missing_kid_list)

            for kid,data in missing_kid_data.items():
                store.put('kid_' + kid, data)

                # This line is needed to get around a pandas warning
                kid_data[kid] = store['kid_' + kid]

        store.close()                
        kid_data = OrderedDict(sorted(kid_data.items(), key=lambda t: t[0]))


        if self.drop_on_quality:
            for kid in kid_data.keys():
                kid_data[kid] = kid_data[kid][kid_data[kid]['SAP_QUALITY'] == 0]
                # kid_data[kid] = kid_data[kid][~pd.isnull(kid_data[kid]['PDCSAP_FLUX'])]

        if self.quarter_list != None:
            kid_data[kid] = kid_data[kid][kid_data[kid]['QUARTER'].isin(self.quarter_list)]
            quarter_list = self.quarter_list            
        else:
            quarter_list = list(range(18))

        
        for quarter in quarter_list:
            data = kid_data[kid].loc[kid_data[kid]['QUARTER'] == quarter, 'PDCSAP_FLUX']
            if len(data) > 0:
                if self.normalize:
                    kid_data[kid].loc[kid_data[kid]['QUARTER'] == quarter, 'PDCSAP_FLUX'] = data / np.nanmedian(data)

                if self.filter_window != None: 
                    data = kid_data[kid][kid_data[kid]['QUARTER'] == quarter].loc[:,'PDCSAP_FLUX']                    
                    kid_data[kid].update(data - trend_util.medianFilter(data, self.filter_window, interpolate=False))

        if self.wrapper_type == 'series':
            return DataWrapper(kid_data)
        elif self.wrapper_type == 'table':
            return DictionaryWrapper(kid_data)
        else:
            print('... Invald wrapper type, defaulting to series ...')
            return DataWrapper(kid_data)
