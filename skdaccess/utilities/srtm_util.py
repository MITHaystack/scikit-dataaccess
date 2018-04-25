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

    pixel_lon_size = (lon_max - lon_min)/(topography.shape[1] - 1)
    pixel_lat_size = (lat_max - lat_min)/(topography.shape[0] - 1)
    topography_extent = (lon_min - 0.5*pixel_lon_size,
                         lon_max + 0.5*pixel_lon_size,
                         lat_min - 0.5*pixel_lat_size,
                         lat_max + 0.5*pixel_lat_size)

    return topography, topography_extent



class SRTMGeolocation(object):
    '''
    This class provides functions to convert between pixel and geodetic coordinates
    '''
    def __init__(self, srtm_data, extents, x_offset=0, y_offset=0, flip_y=True):
        '''
        Initialize SRTM Geolocation object

        @param srtm_data: SRTM data
        @param extents: Latitude and longitude extents
        @param x_offset: Pixel offset in x
        @param y_offset: Pixel offset in y
        @param flip_y: The y axis has been flipped so that increasing
                       y values are increasing in latitude

        '''

        if flip_y == False:
            raise NotImplementedError('Only flipped y axis is currently supported')


        lat_extents = extents[:2]
        lon_extents = extents[2:]

        self.lat_pixel_size = (lat_extents[1] - lat_extents[0]) / srtm_data.shape[0]
        self.lon_pixel_size = (lon_extents[1] - lon_extents[0]) / srtm_data.shape[1]

        self.start_lat = self.lat_pixel_size / 2 + lat_extents[0]
        self.start_lon = self.lon_pixel_size / 2 + lon_extents[0]
        self.x_offset = x_offset
        self.y_offset = y_offset

        self.len_x = srtm_data.shape[1]
        self.len_y = srtm_data.shape[0]

    def getLatLon(self, y, x):
        '''
        Retrive the Latitude and Longitude from pixel coordinates

        @param y: The y pixel
        @param x: The x pixel

        @return (latitude, longitude) of the pixel coordinate
        '''

        lat = self.start_lat + (y + self.y_offset) * self.lat_pixel_size
        lon = self.start_lon + (x + self.x_offset) * self.lon_pixel_size

        return lat, lon

    def getXY(self, lat, lon):
        '''
        Retrive the Latitude and Longitude from pixel coordinates

        @param y: The y pixel
        @param x: The x pixel

        @return (latitude, longitude) of the pixel coordinate
        '''

        y = (lat - self.start_lat) / self.lat_pixel_size - self.y_offset
        x = (lon - self.start_lon) / self.lon_pixel_size - self.x_offset

        return y, x

    def getExtents(self):
        '''
        Retrieve the extents of the data

        @return (minimum_longitude, maximum_longitude, minimum_latitude, maximum_latitude)
        '''
        lat_min, lon_min = self.getLatLon(0,0)
        lat_max, lon_max = self.getLatLon(self.len_y-1, self.len_x-1)

        lon_min -= self.lon_pixel_size/2
        lon_max += self.lon_pixel_size/2
        lat_min -= self.lat_pixel_size/2
        lat_max += self.lat_pixel_size/2

        return lon_min, lon_max, lat_min, lat_max

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

    This method flips the y axis so that increasing y pixels
    are increasing in latitude

    @param srtmdw: SRTM data wrapper
    @param lat_start: Starting latiude
    @param lat_start: Ending latiude
    @param lat_start: Starting longitude
    @param lat_start: Ending longitude

    @return tuple containing the cut data and a geolocation object
    '''

    tiles = getSRTMLatLon(lon_start, lon_end, lat_start, lat_end)
    srtm_data, srtm_extents = merge_srtm_tiles(srtmdw, tiles[2],tiles[3]+1, tiles[0], tiles[1]+1)
    srtm_data = np.flipud(srtm_data)
    srtm_geo = SRTMGeolocation(srtm_data, srtm_extents)

    start_y, start_x = np.round(srtm_geo.getXY(lat_start,lon_start)).astype(np.int)

    end_y, end_x = np.round(srtm_geo.getXY(lat_end,lon_end)).astype(np.int)

    srtm_geo.x_offset = start_x
    srtm_geo.y_offset = start_y

    cut_data = srtm_data[start_y:end_y, start_x:end_x]

    srtm_geo.len_y = cut_data.shape[0]
    srtm_geo.len_x = cut_data.shape[1]

    return cut_data, srtm_geo
