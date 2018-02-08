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


import numpy as np

class SplineLatLon(object):
    '''
    Holds a 2d spline for interpolating lat/lon grid
    '''
    def __init__(self, lat_func, lon_func, x_offset=0, y_offset=0):
        '''
        Initialize SplineLatLon

        @param lat_func: Latitude spline function
        @param lon_func: Longitude spline function
        @param x_offset: Offset in the x coordinate
        @param y_offset: Offset in the y coordinate
        '''
        
        self.lat_func = lat_func
        self.lon_func = lon_func
        self.x_offset = x_offset
        self.y_offset = y_offset

    def __call__(self, y, x):
        '''
        Convert pixel coordinates to lat/lon

        @param y: y coordinate
        @param x: x coordinate

        @return (lat, lon)
        '''

        ret_lat = self.lat_func(y+self.y_offset,x+self.x_offset, grid=False)
        ret_lon = self.lon_func(y+self.y_offset,x+self.x_offset, grid=False)

        if np.isscalar(y) and np.isscalar(x):
            ret_lat = ret_lat.item()
            ret_lon = ret_lon.item()

        return ret_lat, ret_lon

def getExtentsFromCentersPlateCaree(westmost_pixel_lon, eastmost_pixel_lon,
                                    southmost_pixel_lat, northmost_pixel_lat,
                                    lon_grid_spacing, lat_grid_spacing):
    '''
    Given the centers and grid spacing, return the extents of data
    using assuming Plate Caree

    @param westmost_pixel_lon: West most pixel coordinate
    @param eastmost_pixel_lon: East most pixel coordinate
    @param southmost_pixel_lat: South most pixel coordinate
    @param northmost_pixel_lon: North most pixel coordinate

    @return The starting longitude, ending longitude, starting latitude, and ending latitude
    '''

    start_lon = westmost_pixel_lon - lon_grid_spacing/2
    end_lon = eastmost_pixel_lon + lon_grid_spacing/2

    start_lat = southmost_pixel_lat - lat_grid_spacing/2
    end_lat = northmost_pixel_lat + lat_grid_spacing/2


    return (start_lon, end_lon, start_lat, end_lat)
