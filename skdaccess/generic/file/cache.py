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
from skdaccess.framework.data_class import DataFetcherCache, DataWrapperBase

# Standard library imports
from collections import OrderedDict

class DataFetcher(DataFetcherCache):
    '''
    Generic DataFetcher for files
    '''
    
    def __init__(self, ap_paramList=[]):
        '''
        Initialize file data fetcher

        @param ap_paramList[urls]: Autolist of urls to retrieve
        '''
        
        super(DataFetcher, self).__init__(ap_paramList)
            
    def output(self):
        ''' 
        Generate data wrapper for files

        @return FileDataWrapper
        '''
        url_list = self.ap_paramList[0]()
        downloaded_file_list = self.cacheData('files', url_list)

        data_dict = OrderedDict()
        for url, filename in zip(url_list, downloaded_file_list):
            data_dict[url] = filename

        return FileDataWrapper(data_dict)
            

class FileDataWrapper(DataWrapperBase):
    """
    Wrapper for file locations
    """

    def getIterator(self):
        """
        Retrieve an Iteator to the file locations:

        @return Iterator returning (URL, File location)
        """

        return iter(self.data.items())
