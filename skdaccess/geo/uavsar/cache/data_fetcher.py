# The MIT License (MIT)
# Copyright (c) 2018 Massachusetts Institute of Technology
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

# Standard library imports
from collections import OrderedDict
import os

# skdaccess imports
from skdaccess.framework.data_class import DataFetcherCache, ImageWrapper
from skdaccess.utilities.image_util import SplineLatLon
from skdaccess.utilities.uavsar_util import readUAVSARMetadata

# 3rd party imports
import numpy as np


class DataFetcher(DataFetcherCache):
    ''' Data Fetcher for UAVSAR data '''

    def __init__(self, slc_url_list, metadata_url_list, llh_url, memmap):
        '''
        Initialize UAVSAR data fetcher

        @param slc_url_list: List of slc urls
        @param metadata_url_list: List of metadata urls
        @param llh_url: Latitude Longitude Height url
        @param memmap: Open files using a memory map
        '''

        self.slc_url_list = slc_url_list
        self.metadata_url_list = metadata_url_list
        self.llh_url = llh_url
        self.memmap = memmap

        super(DataFetcher, self).__init__()

    def _parseFilename(self, in_filename):
        '''
        Retrive information about UAVSAR data from filename

        @param in_filename: Input filename

        @return information obtained from filename
        '''

        filename = os.path.basename(in_filename)

        filename_info = OrderedDict()

        extension = filename[-3:]
        split_filename = filename[:-4].split('_')

        filename_info['site name'] = split_filename[0]
        filename_info['line ID'] = split_filename[1]
        
        if extension == 'llh':
            
            filename_info['stack number']  = split_filename[2]
            filename_info['baseline correction'] = split_filename[3]
            filename_info['segment number'] = split_filename[4]
            filename_info['downsample factor'] = split_filename[5]

        if extension == 'slc':

            filename_info['flight ID'] = split_filename[2]
            filename_info['data take counter'] = split_filename[3]
            filename_info['acquisition date'] = split_filename[4]

            filename_info['band'] = split_filename[5][0]
            filename_info['steering'] = split_filename[5][1:4]
            filename_info['polarization'] = split_filename[5][4:]

            filename_info['stack_version'] = split_filename[6]
            filename_info['baseline correction'] = split_filename[7]
            filename_info['segment number'] = split_filename[8]
            filename_info['downsample factor'] = split_filename[9]



        filename_info['extension'] = extension
        return filename_info

    def _readUAVSARData(self, filename, metadata, memmap = False):
        '''
        Load UAVSAR data

        @param filename: Input filename
        @param metadata: UAVSAR metadata
        @param memeap: Open file using a memory map

        @return numpy array of data
        '''

        filename_info = self._parseFilename(filename)

        cols = metadata[filename_info['extension'] + '_' + 
                        filename_info['segment number'][1] + '_' + 
                        filename_info['downsample factor'] + 
                        ' Columns']
        
        rows = metadata[filename_info['extension'] + '_' + 
                        filename_info['segment number'][1] + '_' + 
                        filename_info['downsample factor'] + 
                        ' Rows']
        
        if filename_info['extension'] == 'slc':
            dtype = np.dtype('<c8')

        elif filename_info['extension'] == 'llh':
            dtype = np.dtype([('Latitude','<f4'), 
                              ('Longitude','<f4'), 
                              ('Height','<f4')])

        
        if memmap == True:
            return np.memmap(filename, dtype=dtype, mode='r', shape=(rows,cols)), filename_info


        else:
            return np.fromfile(filename, dtype=dtype).reshape(rows,cols), filename_info


    def output(self):
        '''
        Output data as a data wrapper

        @return Imagewrapper of data
        '''

        llh_filename = self.cacheData('uavsar', [self.llh_url])
        filename_list = self.cacheData('uavsar', self.slc_url_list)
        metadata_filename_list = self.cacheData('uavsar', self.metadata_url_list)


        llh,llh_info = self._readUAVSARData(llh_filename[0],
                                            readUAVSARMetadata(metadata_filename_list[0]))
        metadata_dict = OrderedDict()
        data_dict = OrderedDict()
        for filename, metadata_filename in zip(filename_list, metadata_filename_list):
            filename_key = os.path.basename(filename)
            metadata_dict[filename_key] = OrderedDict()

            data_metadata = readUAVSARMetadata(metadata_filename)

            data, data_filename_info = self._readUAVSARData(filename, data_metadata, self.memmap)
            metadata_dict[filename_key]['filename_info'] = data_filename_info
            metadata_dict[filename_key]['metadata'] = data_metadata
            metadata_dict[filename_key]['Latitude'] = llh['Latitude']
            metadata_dict[filename_key]['Longitude'] = llh['Longitude']
            metadata_dict[filename_key]['Height'] = llh['Height']


            data_dict[filename_key] = data

        return ImageWrapper(data_dict, meta_data = metadata_dict)


            
