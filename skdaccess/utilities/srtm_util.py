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

# 3rd party imports
import numpy as np

def merge_srtm_tiles(srtm_tiles, lon_min, lon_max, lat_min, lat_max):
    '''
    Merge the tiles retrieved from the Shuttle Radar Topography Mission data
    using a DataFetcher
    
    @param srtm_tiles: The tiles to merge, contained in an ImageWrapper
    @param lon_min: Minimal longitude used in the DataFectcher
    @param lon_max: Maximal longitude used in the DataFectcher
    @param lat_min: Minimal latitude used in the DataFectcher
    @param lon_min: Maximal latitude used in the DataFectcher

    @return A NumPy array with the merged tiles and its extent in longitude and
            latitude
    '''
    tile = list(srtm_tiles.data.keys())[0]

    tile_width = srtm_tiles.data[tile].shape[1]
    tile_height = srtm_tiles.data[tile].shape[0]

    number_tile_y = abs(lat_max - lat_min)
    number_tile_x = abs(lon_max - lon_min)

    topography = np.empty((tile_height*number_tile_y - (number_tile_y - 1),
                           tile_width*number_tile_x - (number_tile_x - 1)))
    tile_index = 0
    i_factor = 0
    j_factor = number_tile_y - 1
    for i in range(0, number_tile_x):
        for j in range(number_tile_y, 0, -1):
            tile = list(srtm_tiles.data.keys())[tile_index]
            topography[(j - 1)*tile_height - j_factor:j*tile_height - j_factor,
                       i*tile_width - i_factor:(i + 1)*tile_width - i_factor] = srtm_tiles.data[tile]
            tile_index += 1
            j_factor -= 1
        i_factor += 1
        j_factor = number_tile_y - 1

    topography[topography <= 0.] = np.nan

    pixel_lon_size = (lon_max - lon_min)/(topography.shape[1] - 1)
    pixel_lat_size = (lat_max - lat_min)/(topography.shape[0] - 1)
    topography_extent = (lon_min - 0.5*pixel_lon_size,
                         lon_max + 0.5*pixel_lon_size,
                         lat_min - 0.5*pixel_lat_size,
                         lat_max + 0.5*pixel_lat_size)
    
    return topography, topography_extent