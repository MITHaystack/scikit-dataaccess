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
from scipy.interpolate import RectBivariateSpline

class SplineLatLon(object):
    '''
    Holds a 2d spline for interpolating lat/lon grid
    '''
    def __init__(self, lat_func=None, lon_func=None, lat_grid=None, lon_grid=None,
                 x_points=None, y_points=None, lat_extents=None, lon_extents=None,
                 y_num_pixels=None, x_num_pixels=None, x_offset=0, y_offset=0,
                 interp_type='grid'):
        '''
        Initialize SplineLatLon with premade lat/lon functions or information about the latitude and longitude

        @param lat_func: Latitude spline function
        @param lon_func: Longitude spline function
        @param lat_grid: Latitude grid
        @param lon_grid: Longitude grid
        @param x_points: 1d array of x coordinates
        @param y_points: 1d array of y coordinates
        @param lon_extents: Extent of data in longitude
        @param lat_extents: Extent of data in latitude
        @param y_num_pixels: Number of y coordinates
        @param x_num_pixels: Number of x coordinates
        @param x_offset: Offset in the x coordinate
        @param y_offset: Offset in the y coordinate
        @param interp_type: Interpolate type. Currently only 'grid' type is supported
        '''


        if lat_extents is not None and lon_extents is not None and \
           y_num_pixels is not None and x_num_pixels is not None and \
           lat_grid is None and lon_grid is None:

            lat_pixel_size = (lat_extents[1] - lat_extents[0]) / y_num_pixels
            lon_pixel_size = (lon_extents[1] - lon_extents[0]) / x_num_pixels

            lat_coords = np.linspace(lat_extents[0] + 0.5*lat_pixel_size,
                                     lat_extents[1] - 0.5*lat_pixel_size,
                                     num=y_num_pixels, endpoint=True)

            lon_coords = np.linspace(lon_extents[0] + 0.5*lon_pixel_size,
                                     lon_extents[1] - 0.5*lon_pixel_size,
                                     num=x_num_pixels, endpoint=True)

            lon_grid, lat_grid = np.meshgrid(lon_coords, lat_coords)


        if lat_func != None and lon_func != None:
            self.lat_func = lat_func
            self.lon_func = lon_func

        elif lat_grid is not None and lon_grid is not None:

            if x_points==None and y_points==None:
                if interp_type == 'grid':
                    x_points = np.arange(lat_grid.shape[1])
                    y_points = np.arange(lat_grid.shape[0])
                elif 'coords':
                    x_points, y_points = np.meshpoints(np.arange(lat_grid.shape[1]), np.arange(lat_grid.shape[0]))
                else:
                    raise NotImplemented('Only interp_type grid is implemented')

            elif (x_points is None and y_points is not None) or (x_points is not None and y_points is not None):
                raise RuntimeError('Either both x and y points must be specified or neither of them')


            if interp_type=='grid':
                self.lat_func = RectBivariateSpline(y_points, x_points, lat_grid)
                self.lon_func = RectBivariateSpline(y_points, x_points, lon_grid)
            else:
                raise NotImplemented('Only interp_type grid is implemented')



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


def SplineGeolocation(object):
    '''
    This class holds splines to convert between 2d cartesian and geodetic coordinates
    '''
    def __init__(self, lat_spline, lon_spline, x_spline, y_spline, x_offset=0, y_offset=0):

        self.x_offset = x_offset
        self.y_offset = y_offset

        self.lat_spline = lat_spline
        self.lon_spline = lon_spline
        self.x_spline = x_spline
        self.y_spline = y_spline


    def _accessSpline(self, *args, spline_function):
        '''
        Access values from a spline.

        @param *args: Input arguments for spline function
        @param spline_function: Spline function used for interpolation

        @return interpolated values from the spline
        '''
        ret_val = spline_function(*args, grid=False)

        if np.alltrue([np.isscalar([arg for arg in args])]):
            ret_val = ret_val.item()
        else:
            return ret_val



class LinearGeolocation(object):
    '''
    This class provides functions to convert between pixel and geodetic coordinates

    Assumes a linear relationship between pixel and geodetic coordinates
    '''
    def __init__(self, data, extents, x_offset=0, y_offset=0, flip_y=False):
        '''
        Initialize Linear Geolocation object

        @param data: Numpy 2d data
        @param extents: Latitude and longitude extents
        @param x_offset: Pixel offset in x
        @param y_offset: Pixel offset in y
        @param flip_y: The y axis has been flipped so that increasing
                       y values are decreasing in latitude

        '''

        self.flip_y = flip_y

        self.lon_extents = extents[:2]
        self.lat_extents = extents[2:]

        self.lat_pixel_size = (self.lat_extents[1] - self.lat_extents[0]) / data.shape[0]
        self.lon_pixel_size = (self.lon_extents[1] - self.lon_extents[0]) / data.shape[1]

        self.start_lat = self.lat_pixel_size / 2 + self.lat_extents[0]
        self.start_lon = self.lon_pixel_size / 2 + self.lon_extents[0]
        self.x_offset = x_offset
        self.y_offset = y_offset

        self.len_x = data.shape[1]
        self.len_y = data.shape[0]

    def getLatLon(self, y, x):
        '''
        Retrive the latitude and longitude from pixel coordinates

        @param y: The y pixel
        @param x: The x pixel

        @return (latitude, longitude) of the pixel coordinate
        '''

        if self.flip_y:
            y_coord = (self.len_y - y - 1) + self.y_offset

        else:
            y_coord = y + self.y_offset


        lat = self.start_lat + y_coord * self.lat_pixel_size
        lon = self.start_lon + (x + self.x_offset) * self.lon_pixel_size

        return lat, lon

    def getYX(self, lat, lon):
        '''
        Retrive the pixel coordinates from the latitude and longitude

        @param lat: The Latitude
        @param lon: The Longitude

        @return (y, x) pixel coordinates of the input latitude and longitude
        '''

        y = (lat - self.start_lat) / self.lat_pixel_size - self.y_offset
        x = (lon - self.start_lon) / self.lon_pixel_size - self.x_offset



        if self.flip_y:
            y = self.len_y - y - 1

        return y, x

    def getExtents(self):
        '''
        Retrieve the extents of the data

        @return (minimum_longitude, maximum_longitude, minimum_latitude, maximum_latitude)
        '''
        return self.lon_extents + self.lat_extents



def getExtentsFromCentersPlateCarree(westmost_pixel_lon, eastmost_pixel_lon,
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


def convertBinCentersToEdges(bin_centers, dtype = None):
    '''
    Calculate edges of a set of bins from their centers

    @param bin_centers: Array of bin centers
    @param dtype: Data type of array used to store bin edges

    @return bin_edges

    '''

    if dtype is None:
        dtype == bin_centers.dtype

    centers_length = len(bin_centers)
    edges = np.zeros(centers_length + 1, dtype=dtype)
    edges[1:centers_length] = (bin_centers[:-1] + bin_centers[1:]) / 2
    edges[0] = 2*bin_centers[0] - edges[1]
    edges[-1] = 2*bin_centers[-1] - edges[-2]

    return edges


class AffineGlobalCoords(object):
    '''
    Convert between projected and pixel coordinates using an affine transformation
    '''

    def __init__(self, aff_coeffs, center_pixels=False):
        '''
        Initialize Global Coords Object

        @param aff_coeffs: Affine coefficients
        @param center_pixels: Apply offsets so that integer values refer to the
                              center of the pixel and not the edge

        '''

        self._aff_coeffs = aff_coeffs

        if center_pixels:
            self._x_offset = 0.5
            self._y_offset = 0.5

        else:
            self._x_offset = 0.0
            self._y_offset = 0.0


    def getProjectedYX(self, y_array, x_array):
        '''
        Convert pixel coordinates to projected coordinates

        @param y_array: Input y pixel coordinates
        @param x_array: Input x pixel coordinates

        @return projected y coordinates, projected x coordinates
        '''
        y = y_array + self._y_offset
        x = x_array + self._x_offset
        return (self._aff_coeffs[3] + self._aff_coeffs[4]*x + self._aff_coeffs[5]*y,
                self._aff_coeffs[0] + self._aff_coeffs[1]*x + self._aff_coeffs[2]*y)


    def getPixelYX(self, y_proj, x_proj):
        '''
        Convert from projected coordinates to pixel coordinates

        @param y_proj: Input projected y coordinates
        @param x_proj: Input projected x coordinates

        @return y pixel coordinates, x pixel coordinates
        '''
        c0 = self._aff_coeffs[0]
        c1 = self._aff_coeffs[1]
        c2 = self._aff_coeffs[2]
        c3 = self._aff_coeffs[3]
        c4 = self._aff_coeffs[4]
        c5 = self._aff_coeffs[5]


        y = (c4*(c0-x_proj) + c1*y_proj - c1*c3) / (c1*c5 - c2*c4)
        x = -(c5 * (c0 - x_proj) + c2*y_proj - c2*c3) / (c1*c5 - c2*c4)

        return y - self._y_offset, x - self._x_offset

def getGeoTransform(extents, x_size, y_size, y_flipped=True):
    """
    Get 6 geotransform coefficients from the extents of an image and its shape

    Assumes origin is in the upper left and the x pixel coordinate does not depend on
    y projected coordinate, and the y pixl coordinate doesn't depend on the x projected
    coordinate

    @param extents: Image extents (x_min, x_max, y_min, y_max)
    @param x_size: Number of x pixels
    @param y_size: Number of y pixels
    @param y_flipped: The y pixel coordinates are flipped relative
                      to the projected coordinates

    @return list containing the 6 affine transformation coordinates
    """
    x_res = (extents[1] - extents[0]) / x_size
    y_res = (extents[3] - extents[2]) / y_size

    geo_transform = []
    geo_transform.append(extents[0])
    geo_transform.append(x_res)
    geo_transform.append(0)
    geo_transform.append(extents[-1])
    geo_transform.append(0)
    geo_transform.append(y_res)

    if y_flipped == True:
        geo_transform[-1] *= -1

    return geo_transform
