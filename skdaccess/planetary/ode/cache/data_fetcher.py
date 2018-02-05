# The MIT License (MIT)
# Copyright (c) 2018 Massachusetts Institute of Technology
#
# Author: Guillaume Rongier
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

# Scikit Data Access imports
from skdaccess.framework.data_class import DataFetcherCache, ImageWrapper
from skdaccess.utilities.ode_util import *

# 3rd party imports
import pandas as pd
import numpy as np
from osgeo import gdal

# Standard library imports
from collections import OrderedDict
import os

class DataFetcher(DataFetcherCache):
    ''' Data Fetcher from the Orbital Data Explorer (ODE) '''

    def __init__(self, target, mission, instrument, product_type,
                 western_lon = None, eastern_lon = None, min_lat = None, max_lat = None,
                 min_ob_time = '', max_ob_time = '', product_id = '', file_name = '*',
                 number_product_limit = 10, result_offset_number = 0, remove_ndv = True):

        '''
        Construct Data Fetcher object
        For more information about the different fields and the possible values,
        see the manual of ODE REST interface at http://oderest.rsl.wustl.edu

        @param target: Aimed planetary body, i.e., Mars, Mercury, Moon, Phobos, or Venus
        @param mission: Aimed mission, e.g., MGS or MRO
        @param instrument: Aimed instrument from the mission, e.g., HIRISE or CRISM
        @param product_type: Type of product to look for, e.g., DTM or RDRV11
        @param western_lon: Western longitude to look for the data, from 0 to 360
        @param eastern_lon: Eastern longitude to look for the data, from 0 to 360
        @param min_lat: Minimal latitude to look for the data, from -90 to 90
        @param max_lat: Maximal latitude to look for the data, from -90 to 90
        @param min_ob_time: Minimal observation time in (even partial) UTC format, e.g., '2017-03-01'
        @param max_ob_time: Maximal observation time in (even partial) UTC format, e.g., '2017-03-01'
        @param product_id: PDS Product ID to look for, with wildcards (*) allowed
        @param file_name: File name to look for, with wildcards (*) allowed
        @param number_product_limit: Maximal number of products to return (ODE allows 100 at most)
        @param result_offset_number: Offset the return products, to go beyond the limit of 100 returned products
        @param remove_ndv: Replace the no-data value as mentionned in the label by np.nan
        '''
        
        assert western_lon is None or 0. <= western_lon <= 360., 'Western longitude is not between 0 and 360 degrees'
        assert eastern_lon is None or 0. <= eastern_lon <= 360., 'Eastern longitude is not between 0 and 360 degrees'
        assert min_lat is None or -90. <= min_lat <= 90., 'Minimal latitude is not between -90 and 90 degrees'
        assert max_lat is None or -90. <= max_lat <= 90., 'Maximal latitude is not between -90 and 90 degrees'
        assert 1 <= number_product_limit <= 100, 'Number of product limit must be between 1 and 100'
        
        self.target = target
        self.mission = mission
        self.instrument = instrument
        self.product_type = product_type
        self.western_lon = western_lon
        self.eastern_lon = eastern_lon
        self.min_lat = min_lat
        self.max_lat = max_lat
        self.min_ob_time = min_ob_time
        self.max_ob_time = max_ob_time
        self.product_id = product_id
        self.file_name = file_name
        self.number_product_limit = number_product_limit
        self.result_offset_number = result_offset_number
        self.remove_ndv = remove_ndv

    def output(self):
        '''
        Generate data wrapper from ODE data
        '''

        file_urls = query_files_urls(self.target, self.mission, self.instrument, self.product_type,
                                     self.western_lon, self.eastern_lon, self.min_lat, self.max_lat,
                                     self.min_ob_time, self.max_ob_time, self.product_id, self.file_name,
                                     self.number_product_limit, self.result_offset_number)

        downloaded_files = self.cacheData('ode', file_urls.keys())

        # Gather the data and meta-data
        data_dict = OrderedDict()
        metadata_dict = OrderedDict()
        unopened_files = []
        opened_files = []
        unlabeled_files = []
        for file, key in zip(downloaded_files, file_urls.keys()):
            file_description = file_urls.get(key)[1]
            if 'LABEL' in file_description or 'IMG' in file_description:
                label = file.split('/')[-1]
                product = file_urls.get(key)[0]
                if metadata_dict.get(product, None) is None:
                    data_dict[product] = OrderedDict()
                    metadata_dict[product] = OrderedDict()
                    metadata_dict[product]['Unopened files'] = []
                raster = gdal.Open(file)
                # Try to correct the label file
                if raster is None:
                    new_label_file = correct_label_file(file, downloaded_files)
                    raster = gdal.Open(new_label_file)
                    if raster is not None:
                        print('File', label, 'has been corrected')
                # If the file still cannot be opened, deal with it later
                if raster is None:
                    unopened_files.append((file, product))
                # Otherwise, put the data in a NumPy array and get the meta-data
                else:
                    opened_files.append((file, product))
                    raster_array = get_raster_array(raster, remove_ndv = self.remove_ndv)
                    data_dict[product][label] = raster_array
                    metadata_dict[product][label] = OrderedDict()
                    metadata_dict[product][label]['Geotransform'] = raster.GetGeoTransform()
                    metadata_dict[product][label]['Projection'] = raster.GetProjection()
                    metadata_dict[product][label]['Pixel sizes'] = (raster.GetGeoTransform()[1],
                                                          raster.GetGeoTransform()[5])
                    metadata_dict[product][label]['Extent'] = get_raster_extent(raster)
                    # Close the data
                    raster = None
            else:
                label = file.split('/')[-1]
                product = file_urls.get(key)[0]
                unlabeled_files.append((file, product))

        # Put the unopened files' local address with the meta-data, so that the 
        # user can decide what to do with them. It implies to look for the 
        # companion files of the label files that could not be opened.
        for file, product in unopened_files:
            companion_files = [file]
            print('File', file.split('/')[-1], 'could not be opened')
            for file_2, product_2 in unlabeled_files:
                if (product_2 == product
                    and '.'.join(file_2.split('/')[-1].split('.')[:-1]) == '.'.join(file.split('/')[-1].split('.')[:-1])):
                    companion_files.append(file_2)
                    print('File', file_2.split('/')[-1], 'could not be opened')
            metadata_dict[product]['Unopened files'].append(companion_files)
        for file, product in unlabeled_files:
            companion_files = []
            for file_2, product_2 in opened_files + unopened_files:
                if (product_2 == product
                    and '.'.join(file_2.split('/')[-1].split('.')[:-1]) == '.'.join(file.split('/')[-1].split('.')[:-1])):
                    companion_files.append(file_2)
            if len(companion_files) == 0:
                print('File', file.split('/')[-1], 'could not be opened')
                metadata_dict[product]['Unopened files'].append([file])                

        return ImageWrapper(obj_wrap = data_dict, meta_data = metadata_dict)
