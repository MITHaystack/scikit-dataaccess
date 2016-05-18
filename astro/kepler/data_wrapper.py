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

# """@package Kepler DataWrapper
# Provides Data classes for Kepler data for use in the Computer-Aided Discovery pipeline.
# """

# mithagi required Base,Utils imports
from skdaccess.framework.data_class import DataWrapperBase
# 3rd party package imports

       
class DataWrapper(DataWrapperBase):
    ''' Data wrapper for kepler light curve data '''

    def getIterator(self):
        '''
        Retrieve an iterator to the data.
        
        @return Iterator to the Kepler Data (label, data, error)
        '''
        for keplerid in self.data.keys():
            yield keplerid, self.data[keplerid].loc[:,'PDCSAP_FLUX'], self.data[keplerid].loc[:,'PDCSAP_FLUX_ERR']
