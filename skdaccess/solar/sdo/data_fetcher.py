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
from skdaccess.framework.data_class import DataFetcherStream, ImageWrapper
from skdaccess.framework.param_class import *


# Standard library imports
from collections import OrderedDict

# 3rd part imports
from six.moves.urllib.request import urlopen
from skimage.io import imread
from astropy.io import fits
import warnings

class DataFetcher(DataFetcherStream):
    '''
    Data Fetcher for the Solar Dynamics Observatory
    '''
    
    def __init__(self, ap_paramList):
        '''
        Initialize Solar Dynamics Observatory

        @param ap_paramList[url_list]: Autolist of URLS to access
        '''
        super(DataFetcher, self).__init__(ap_paramList)

    def output(self):
        '''
        Generate data wrapper

        @return data wrapper of SDO data
        '''
        url_list = self.ap_paramList[0]()

        metadata, data = self.retrieveOnlineData(url_list)

        return ImageWrapper(data, meta_data = metadata)

