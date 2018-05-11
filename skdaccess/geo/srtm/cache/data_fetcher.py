# The MIT License (MIT)
# Copyright (c) 2016 Massachusetts Institute of Technology
#
# Authors: Cody Rude, Guillaume Rongier
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
from skdaccess.utilities.support import convertToStr
from skdaccess.utilities.image_util import getExtentsFromCentersPlateCarree, LinearGeolocation, convertBinCentersToEdges


# 3rd party imports
import pandas as pd
import numpy as np
from pkg_resources import resource_filename

# Standard library imports
from collections import OrderedDict
from calendar import monthrange
from zipfile import ZipFile
import os


class DataFetcher(DataFetcherCache):
    ''' DataFetcher for retrieving data from the Shuttle Radar Topography Mission '''
    def __init__(self, lat_tile_start, lat_tile_end, lon_tile_start, lon_tile_end,
                 username, password, arcsecond_sampling = 1, mask_water = True):
        '''
        Initialize Data Fetcher

        @param lat_tile_start: Latitude of the southwest corner of the starting tile
        @param lat_tile_end: Latitude of the southwset corner of the last tile
        @param lon_tile_start: Longitude of the southwest corner of the starting tile
        @param lon_tile_end: Longitude of the southwest corner of the last tile
        @param username: NASA Earth Data username
        @param password: NASA Earth Data Password
        @param arcsecond_sampling: Sample spacing of the SRTM data, either 1 arc-
                                   second or 3 arc-seconds
        @param mask_water: True if the water bodies should be masked, false otherwise
        '''
        assert arcsecond_sampling == 1 or arcsecond_sampling == 3, "Sampling should be 1 or 3 arc-seconds"

        self.lat_tile_start = lat_tile_start
        self.lat_tile_end = lat_tile_end
        self.lon_tile_start = lon_tile_start
        self.lon_tile_end = lon_tile_end
        self.username = username
        self.password = password
        self.arcsecond_sampling = arcsecond_sampling
        self.mask_water = mask_water
        
        super(DataFetcher, self).__init__()

    def output(self):
        '''
        Generate SRTM data wrapper

        @return SRTM Image Wrapper
        '''

        lat_tile_array = np.arange(self.lat_tile_start, self.lat_tile_end+1)
        lon_tile_array = np.arange(self.lon_tile_start, self.lon_tile_end+1)

        lat_grid,lon_grid = np.meshgrid(lat_tile_array, lon_tile_array)

        lat_grid = lat_grid.ravel()
        lon_grid = lon_grid.ravel()

        
        filename_root = '.SRTMGL1.'
        base_url = 'https://e4ftl01.cr.usgs.gov/MEASURES/'
        folder_root = 'SRTMGL1.003/2000.02.11/'
        if self.arcsecond_sampling == 3:
            filename_root = '.SRTMGL3.'
            folder_root = 'SRTMGL3.003/2000.02.11/'
        base_url += folder_root

        filename_list = []
        for lat, lon in zip(lat_grid, lon_grid):

            if lat < 0:
                lat_label = 'S'
                lat = np.abs(lat)
            else:
                lat_label = 'N'

            if lon < 0:
                lon_label = 'W'
                lon = np.abs(lon)
            else:
                lon_label = 'E'

            filename_list.append(lat_label + convertToStr(lat, 2) + lon_label + convertToStr(lon, 3) + filename_root + 'hgt.zip')
            if self.mask_water == True:
                filename_list.append(lat_label + convertToStr(lat, 2) + lon_label + convertToStr(lon, 3) + filename_root + 'num.zip')

        # Read in list of available data
        srtm_list_filename = 'srtm_gl1.txt'
        if self.arcsecond_sampling == 3:
            srtm_list_filename = 'srtm_gl3.txt'
        srtm_support_filename = resource_filename('skdaccess', os.path.join('support',srtm_list_filename))
        available_file_list = open(srtm_support_filename).readlines()
        available_file_list = [filename.strip() for filename in available_file_list]

        requested_files = pd.DataFrame({'Filename' : filename_list})
        requested_files['Valid'] = [ '.'.join(filename.split('.')[0:-2]) in available_file_list for filename in filename_list ]
        valid_filename_list = requested_files.loc[ requested_files['Valid']==True, 'Filename'].tolist()
        url_list = [base_url + filename for filename in valid_filename_list]
        downloaded_file_list = self.cacheData('srtm', url_list, self.username, self.password,
                                                  'https://urs.earthdata.nasa.gov')
        requested_files.loc[ requested_files['Valid']==True, 'Full Path'] = downloaded_file_list

        def getCoordinates(filename):
            '''
            Determine the longitude and latitude of the lowerleft corner of the input filename

            @param in_filename: Input SRTM filename
            @return Latitude of southwest corner, Longitude of southwest corner
            '''

            lat_start = int(filename[1:3])
            
            if filename[0] == 'S':
                lat_start *= -1

            lon_start = int(filename[4:7])

            if filename[3] == 'W':
                lon_start *= -1

            return lat_start, lon_start


        data_dict = OrderedDict()
        metadata_dict = OrderedDict()
        
        array_shape = (3601,3601)
        if self.arcsecond_sampling == 3:
            array_shape = (1201,1201)
        
        file_slice = slice(None)
        water_value = 0
        if self.mask_water == True:
            file_slice = slice(0, -1, 2)
            water_value = np.nan

        for i in requested_files.index[file_slice]:
            
            hgt_full_path = requested_files.at[i, 'Full Path']
            hgt_filename = requested_files.at[i, 'Filename']

            if requested_files.at[i, 'Valid']:

                masked_dem_data = np.ones(array_shape)
                if self.mask_water == True and requested_files.at[i + 1, 'Valid']:
                    
                    num_full_path = requested_files.at[i + 1, 'Full Path']
                    num_filename = requested_files.at[i + 1, 'Full Path']
                    
                    zipped_num_data = ZipFile(num_full_path)
                    zipped_num_full_path = zipped_num_data.infolist()[0].filename

                    num_data = np.frombuffer(zipped_num_data.open(zipped_num_full_path).read(),
                                             np.dtype('uint8')).reshape(array_shape)
                    masked_dem_data[(num_data == 1) | (num_data == 2)] = water_value
                    
                    i += 1

                zipped_hgt_data = ZipFile(hgt_full_path)
                zipped_hgt_full_path = zipped_hgt_data.infolist()[0].filename

                dem_data = np.frombuffer(zipped_hgt_data.open(zipped_hgt_full_path).read(),
                                         np.dtype('>i2')).reshape(array_shape)
                masked_dem_data *= dem_data

            else:

                masked_dem_data = np.full(shape=array_shape, fill_value=water_value)
                
                i += 1


            label = hgt_filename[:7]

            data_dict[label] = masked_dem_data

            lat_start, lon_start = getCoordinates(hgt_filename)

            lat_coords, lon_coords = np.meshgrid(np.linspace(lat_start+1, lat_start, array_shape[0]),
                                                 np.linspace(lon_start, lon_start+1, array_shape[1]),
                                                 indexing = 'ij')

            metadata_dict[label] = OrderedDict()
            metadata_dict[label]['Latitude'] = lat_coords
            metadata_dict[label]['Longitude'] = lon_coords

            
            lon_edges = convertBinCentersToEdges(lon_coords[0,:])
            lat_edges = convertBinCentersToEdges(lat_coords[::-1,0])

            extents = [lon_edges[0], lon_edges[-1], lat_edges[0], lat_edges[-1]]
            

            metadata_dict[label]['Geolocation'] = LinearGeolocation(masked_dem_data, extents, flip_y=True)
            
        
        return ImageWrapper(obj_wrap = data_dict, meta_data = metadata_dict)
