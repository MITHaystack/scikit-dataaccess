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

# Standard library imports
from collections import OrderedDict

# Skdaccess imports
from skdaccess.framework.data_class import DataFetcherBase, ImageWrapper

# 3rd party imports
import h5py



class DataFetcher(DataFetcherBase):
    '''
    Generic data fetcher for loading images from a hdf file
    '''

    def __init__(self, dataset_dict, verbose=False):
        '''
        Initialize DataFetcher

        @param dictionary where the keys are filenames and the values are the dataset names
        @param verbose: Output extra debug information
        '''
        self.dataset_dict = dataset_dict
        
        super(DataFetcher, self).__init__([], verbose)


    def output(self):
        '''
        Output data wrapper

        @return Image Data Wrapper
        '''
        data_dict = OrderedDict()
        metadata_dict = OrderedDict()

        for filename, dataset_list in self.dataset_dict.items():

            h5_file = h5py.File(filename, mode='r')

            for dataset_name in dataset_list:
                data_label = filename + ': ' + dataset_name
                data_dict[data_label] = h5_file[dataset_name][:]
                metadata_dict[data_label] = OrderedDict()
                metadata_dict[data_label]['filename'] = filename
                metadata_dict[data_label]['dataaset_name'] = dataset_list

        return ImageWrapper(data_dict)

    
