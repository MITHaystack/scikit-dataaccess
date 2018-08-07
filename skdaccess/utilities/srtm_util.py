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
from .image_util import AffineGlobalCoords, getGeoTransform

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

    pixel_lon_size = (lon_max - lon_min)/(topography.shape[1] - 1)
    pixel_lat_size = (lat_max - lat_min)/(topography.shape[0] - 1)
    topography_extent = (lon_min - 0.5*pixel_lon_size,
                         lon_max + 0.5*pixel_lon_size,
                         lat_min - 0.5*pixel_lat_size,
                         lat_max + 0.5*pixel_lat_size)

    return topography, topography_extent




def getSRTMLatLon(lat_min, lat_max, lon_min, lon_max):
    '''
    Retrieve parameters that encompass area when creating SRTM data fetcher.

    @param lat_min: Minimum latitude
    @param lat_max: Maximum latitude
    @param lon_min: Minimum longitude
    @param lon_max: Maximum longitude

    @return (starting_latitude, ending_latitude,
             starting_longitude, ending_longitude)
    '''

    start_lat = int(np.floor(lat_min))
    start_lon = int(np.floor(lon_min))
    end_lat = int(np.floor(lat_max))
    end_lon = int(np.floor(lon_max))

    return start_lat, end_lat, start_lon, end_lon


def getSRTMData(srtmdw, lat_start,lat_end, lon_start,lon_end):
    '''
    Select SRTM data in a latitude/longitude box

    @param srtmdw: SRTM data wrapper
    @param lat_start: Starting latiude
    @param lat_end: Ending latiude
    @param lon_start: Starting longitude
    @param lon_end: Ending longitude
    @param flip_y: Flip the y axis so that increasing y pixels are increasing in latitude

    @return Tuple containing the cut data, new extents, and a affine geotransform coefficients
    '''

    tiles = getSRTMLatLon(lat_start, lat_end, lon_start, lon_end)
    srtm_data, srtm_extents = merge_srtm_tiles(srtmdw, tiles[2],tiles[3]+1, tiles[0], tiles[1]+1)

    full_geotransform = getGeoTransform(srtm_extents, srtm_data.shape[1], srtm_data.shape[0])

    full_geo = AffineGlobalCoords(full_geotransform)

    start_y, start_x = np.floor(full_geo.getPixelYX(lat_end,lon_start)).astype(np.int)

    end_y, end_x = np.ceil(full_geo.getPixelYX(lat_start,lon_end)).astype(np.int)

    cut_data = srtm_data[start_y:end_y, start_x:end_x]

    cut_proj_y_start, cut_proj_x_start = full_geo.getProjectedYX(end_y, start_x)
    cut_proj_y_end, cut_proj_x_end = full_geo.getProjectedYX(start_y, end_x)

    cut_extents = [
        cut_proj_x_start,
        cut_proj_x_end,
        cut_proj_y_start,
        cut_proj_y_end
    ]

    cut_geotransform = full_geotransform.copy()
    cut_geotransform[0] = cut_extents[0]
    cut_geotransform[3] = cut_extents[-1]

    return cut_data, cut_extents, cut_geotransform
