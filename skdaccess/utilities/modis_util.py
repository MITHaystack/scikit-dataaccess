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


# skdaccess imports 
# Standard library imports
import ast
import os
import xml.etree.ElementTree as ET
from collections import OrderedDict

# 3rd party imports
import numpy as np
from netCDF4 import Dataset
from scipy.interpolate import RectBivariateSpline
from scipy.optimize import brute
from six.moves.urllib.request import urlopen
from skdaccess.framework.data_class import ImageWrapper

def getImageType(in_data):
    '''
    Determine what type of modis data is being processed

    There are 3 array shapes we deal with:
    @verbatim
    mode 1 -> (y, x, z)
    mode 2 -> (y, x)
    mode 3 -> (z, y ,x)
    @endverbatim
    where z axis represents different data products
    and y and x correspond to the y and x image
    coordinates from the modis instrument

    @param in_data: Input modis data
    @return type of modis data
    '''

    if len(in_data.shape) == 2:
        mode = 2
    elif in_data.shape[0] > in_data.shape[2]:
        mode = 1
    elif in_data.shape[0] < in_data.shape[2]:
        mode = 3
    else:
        raise RuntimeError("Data shape not understood")

    return mode


def calibrateModis(data, metadata):
    '''
    This function calibrates input modis data

    @param data: Input modis data
    @param metadata: Metadata associated with modis input data

    @return calibrated modis data
    '''

    # This function is used for flipping MODIS data
    def flip_data(data, mode):
        
        if mode in (1,2):
            return np.flipud(np.fliplr(data))

        elif mode == 3:
            return np.flip(np.flip(data,axis=1), axis=2)

        else:
            raise ValueError("Mode " + str(mode) + " not understood")


    sds_names = metadata['sds_names']
    product_id = metadata['product_id']
    platform = metadata['platform']

    mode = getImageType(data)    
        
    if platform.lower() == 'myd':
        data = flip_data(data, mode)
        metadata['Latitude'] = flip_data(metadata['Latitude'], 2)
        metadata['Longitude'] = flip_data(metadata['Longitude'], 2)
        

    def levelTwoInfo(info):
        fill_value = info['_FillValue']
        add_offset = info['add_offset']
        scale_factor = info['scale_factor']

        return add_offset, scale_factor, fill_value


    if product_id.upper() in ('09','06_L2'):

        new_data = data.astype(np.float)
        for index, key in enumerate(sds_names):

            add_offset, scale_factor, fill_value = levelTwoInfo(metadata[key])

            if product_id.upper() == '09':
                scale_factor = 1.0/scale_factor

            if mode == 1:
                new_data[:,:,index] = scale_factor * (new_data[:,:,index] - add_offset)
            elif mode == 2:
                new_data = scale_factor * (new_data - add_offset)
            else:
                raise RuntimeError('Data has wrong number of dimensions')

    elif product_id.upper() in ['35_L2']:
        for index, key in enumerate(sds_names):
            # 35_L2 should require no calibration
            add_offset, scale_factor, fill_value = levelTwoInfo(metadata[key])
            if not (np.isclose(fill_value, 0) and np.isclose(scale_factor,1) and np.isclose(add_offset,0)):
                raise RuntimeError('Unexpected calibration data for 35_L2')

        new_data = data

    else:
        raise RuntimeError('Calibration of product ' + product_id + ' not supported')

    return new_data


def rescale(in_array, max_val=0.9,min_val = -0.01):
    '''
    This function rescales an image to fall between 0 and 1

    @param in_array: Data to be rescaled
    @param max_val: Values greater than or equal to max_val will become 1
    @param min_val: Values less than or equal to min_val will become 0

    @return scaled data
    '''

    new_array = (in_array - min_val) / (max_val - min_val)
    new_array[new_array>1.0] = 1.0
    new_array[new_array<0.0] = 0.0
    
    return new_array



            

class LatLon(object):
    ''' Calculates Lat/Lon position from y,x pixel coordinate '''

    def __init__(self, metadata, x_offset = 0, y_offset = 0):

        ''' 
        Initialize getLatLon object

        @param metadata: Image metadata
        @param x_offset: Pixel offset (used when gridding data)
        @param y_offset: Pixel offset (used when gridding data)
        '''

        self.x_offset = x_offset
        self.y_offset = y_offset

        ylen = metadata['y_size']
        xlen = metadata['x_size']

        sublat = metadata['Latitude']
        sublon = metadata['Longitude']

        lat_metadata = metadata['Latitude_Metadata']
        lon_metadata = metadata['Longitude_Metadata']
        


        if sublat.shape == (ylen, xlen):
            # the size of the lat/lon grids
            # matches the data size
            # Save lat/lon grids
            self.lat_data = sublat
            self.lon_data = sublon

            # create x and y coords
            y = np.arange(sublat.shape[0])
            x = np.arange(sublat.shape[1])

            # Interpolation between pixels
            self.alat = RectBivariateSpline(y, x, sublat)
            self.alon = RectBivariateSpline(y, x, sublon)


        else:
            # lat and lon grids don't match size of data

            self.lat_data = None
            self.lon_data = None

            # Metadata for lat/lon sampling of data
            try:
                lat_x_sampling = [int(x) for x in lat_metadata['Cell_Across_Swath_Sampling'].split(', ')]
                lat_y_sampling = [int(y) for y in lat_metadata['Cell_Along_Swath_Sampling'].split(', ')]
                lon_x_sampling = [int(x) for x in lon_metadata['Cell_Across_Swath_Sampling'].split(', ')]
                lon_y_sampling = [int(y) for y in lon_metadata['Cell_Along_Swath_Sampling'].split(', ')]

            # Data product does not provide sampling information...
            except KeyError:
                if lat_metadata['frame_numbers'] == '3,8,13,...' and \
                   lon_metadata['line_numbers'] == '3,8':
                    lat_x_sampling = [3, xlen, 5]
                    lat_y_sampling = [3, ylen, 5]
                    lon_x_sampling = [3, xlen, 5]
                    lon_y_sampling = [3, ylen, 5]
                else:
                    raise RuntimeError('Cannot parse lat/lon Metadata')

            # metadata is an array, not a string
            except AttributeError:
                lat_x_sampling = lat_metadata['Cell_Across_Swath_Sampling']
                lat_y_sampling = lat_metadata['Cell_Along_Swath_Sampling']
                lon_x_sampling = lon_metadata['Cell_Across_Swath_Sampling']
                lon_y_sampling = lon_metadata['Cell_Along_Swath_Sampling']
                    

            # seems information starts indexing at 1
            lat_x_sampling[0] = lat_x_sampling[0] - 1
            lat_y_sampling[0] = lat_y_sampling[0] - 1
            lon_x_sampling[0] = lon_x_sampling[0] - 1
            lon_y_sampling[0] = lon_y_sampling[0] - 1

            # Generate grids for interpolation
            laty = np.arange(*lat_y_sampling)
            latx = np.arange(*lat_x_sampling)
            lony = np.arange(*lon_y_sampling)
            lonx = np.arange(*lon_x_sampling)


            # Interpolation
            self.alat = RectBivariateSpline(laty,latx,sublat)
            self.alon = RectBivariateSpline(lony,lonx,sublon)


    def __call__(self, y, x):
        ''' 
        Convert pixel coordinates to lat/lon
        
        @param y: y coordinate
        @param x: x coordinate
        
        @return (lat, lon)
        '''
        

        # # If interpolation of geodata is necessary
        # if self.lat_data is None:

        ret_lat = self.alat(y+self.y_offset,x+self.x_offset, grid=False)
        ret_lon = self.alon(y+self.y_offset,x+self.x_offset, grid=False)

        if np.isscalar(y) and np.isscalar(x):
            ret_lat = ret_lat.item()
            ret_lon = ret_lon.item()

        return ret_lat, ret_lon

        # # If geodata is the same resolution as science data
        # else:
        #     return self.lat_data[y,x], self.lon_data[y,x]


# Utility function to retrieve the value of a bit in a bit flag
def checkBit(data,bit):
    '''
    Get the bit value from a bit flag

    @param data: Integer bit flag
    @param bit: Which bit to select (start indexing at 0)

    @return value of chosen bit in bit flag
    '''
    
    return 1 & (data >> bit)



def createGrid(data, y_start, y_end, x_start, x_end, y_grid, x_grid, dtype, grid_fill = np.nan):
    '''
    Subsets image data into a smaller image

    Takes care to make sure the resulting subsection
    has the expected size by filling in missing data

    @param data: Input data
    @param y_start: Starting pixel for y
    @param y_end: Ending pixel for y
    @param x_start: Starting pixel x
    @param x_end: Ending pixel for x
    @param y_grid: Grid size for y
    @param x_grid: Grid size for x
    @param dtype: The dtype of the new grid data
    @param grid_fill: Fill value to use when there is no data

    @return image subsection, fraction of valid data
    '''

    mode = getImageType(data)


    fraction = 1.0

    if mode == 1:
        section_slice = (slice(y_start,y_end), slice(x_start,x_end),slice(None))
        section = data[section_slice]
        fraction = np.prod(section.shape[:2]) / (y_grid*x_grid)
        new_data = np.zeros((y_grid,x_grid, section.shape[2]), dtype = dtype)
        new_data_slice1 = (slice(section.shape[0], None), slice(None),                   slice(None))
        new_data_slice2 = (slice(None),                   slice(section.shape[1], None), slice(None))
        new_data_slice3 = (slice(None, section.shape[0]), slice(None, section.shape[1]), slice(None))
        section_y_len = section.shape[0]
        section_x_len = section.shape[1]

    elif mode == 2:
        section_slice = (slice(y_start,y_end), slice(x_start,x_end))
        section = data[section_slice]
        fraction = np.prod(section.shape) / (y_grid*x_grid)
        new_data = np.zeros((y_grid,x_grid), dtype = dtype)
        new_data_slice1 = (slice(section.shape[0], None), slice(None))
        new_data_slice2 = (slice(None),                   slice(section.shape[1], None))
        new_data_slice3 = (slice(None, section.shape[0]), slice(None, section.shape[1]))
        section_y_len = section.shape[0]
        section_x_len = section.shape[1]


    elif mode == 3:
        section_slice = (slice(None), slice(y_start,y_end), slice(x_start,x_end))
        section = data[section_slice]
        fraction = np.prod(section.shape[1:]) / (y_grid*x_grid)
        new_data = np.zeros((y_grid,x_grid, section.shape[2]), dtype = dtype)
        new_data_slice1 = (slice(None), slice(section.shape[0], None), slice(None))
        new_data_slice2 = (slice(None), slice(None),                   slice(section.shape[1], None))
        new_data_slice3 = (slice(None, section.shape[0]), slice(None, section.shape[1]), slice(None, section.shape[2]))
        section_y_len = section.shape[1]
        section_x_len = section.shape[2]

    else:
        raise ValueError('mode value not understood')


    if (y_grid * x_grid) != (section_y_len * section_x_len):

        new_data[new_data_slice1] = grid_fill
        new_data[new_data_slice2] = grid_fill

    new_data[new_data_slice3] = section.astype(new_data.dtype)

    return new_data, fraction

def getFileIDs(modis_identifier, start_date, end_date, lat, lon, daynightboth):
    '''
    Retrieve file IDs for images matching search parameters

    @param modis_identifier: Product identifier (e.g. MOD09)
    @param start_date: Starting date
    @param end_date: Ending date
    @param lat: Latitude 
    @param lon: Longitude
    @param daynightboth: Get daytime images ('D'), nightime images ('N') or both ('B')

    @return list of file IDs
    '''

    lat_str = str(lat)
    lon_str = str(lon)
    
    info_url = ('https://modwebsrv.modaps.eosdis.nasa.gov/axis2/services/MODAPSservices/searchForFiles'
                    + '?product=' + modis_identifier + '&collection=6&start=' + start_date
                    + '&stop=' + end_date + '&north=' + lat_str + '&south=' + lat_str + '&west='
                    + lon_str + '&east=' + lon_str + '&coordsOrTiles=coords&dayNightBoth=' + daynightboth)

    url = urlopen(info_url)
    tree = ET.fromstring(url.read().decode())
    url.close()

    return [ int(child.text) for child in tree ]

def getFileURLs(file_ids):
    '''
    Retrieve the ftp location for a list of file IDs

    @param file_ids: List of file IDs
    @return List of ftp locations
    '''
    


    info_url='http://modwebsrv.modaps.eosdis.nasa.gov/axis2/services/MODAPSservices/getFileUrls?fileIds='

    for file_id in file_ids:
        info_url += str(file_id) + ','

    info_url = info_url[:-1]


    url = urlopen(info_url)
    tree = ET.fromstring(url.read().decode())
    url.close()

    return [ child.text for child in tree ]

def getModisData(dataset, variable_name):
    '''
    Loads modis data

    @param dataset: netCDF4 dataset
    @param variable_name: Name of variable to extract from dataset

    @return (modis_data, metadata)
    '''

    variable = dataset[variable_name]
    variable.set_auto_maskandscale(False)
    data = variable[:,:]
    metadata = OrderedDict()
    for attribute in variable.ncattrs():
        metadata[attribute] = variable.getncattr(attribute)

    return data,metadata
     
 
def readMODISData(modis_list, variables, grid, grid_fill, use_long_name, platform, product_id):
    '''
    Retrieve a list of modis data

    @param modis_list: List of MODIS data to load
    @param variables: List of variables in the MODIS data to load 
    @param grid: Further divide each image into a multiple grids of size (y,x)
    @param grid_fill: Fill value to use when creating gridded data 
    @param use_long_name: Use long names for metadata instead of variable name
    @param platform: Which satellite to use, either MOD or MYD.
    @param product_id: Product string (e.g. '06_L2')
    '''

    metadata_dict = OrderedDict()
    data_dict = OrderedDict()
    for modis_location in modis_list:
        combined_metadata = OrderedDict()
        combined_data = []

        # Open data set
        full_data = Dataset(modis_location)

        # Get full metadata
        full_metadata = OrderedDict()

        for key in full_data.ncattrs():
            full_metadata[key] = full_data.getncattr(key)

        # Read in science data
        for variable_name in variables:

            data, metadata = getModisData(full_data, variable_name)
            if use_long_name:
                sds_name = metadata['long_name']
            else:
                sds_name = variable_name
                
            combined_metadata[sds_name] = metadata
            combined_data.append(data)

        sds_names_list = list(combined_metadata.keys())

        combined_metadata['sds_names'] = sds_names_list
        combined_metadata['collection_metadata'] = full_metadata
        combined_metadata['product_id'] = product_id
        combined_metadata['platform'] = platform
            
            
        if len(combined_data) > 1:
            if len(combined_data[0].shape) == 2:
                data = np.dstack(combined_data)
            else:
                data = np.concatenate(combined_data,axis=2)

        # Read in geolocation data
        sublat, sublat_meta = getModisData(full_data, 'Latitude')
        sublon, sublon_meta = getModisData(full_data, 'Longitude')

        combined_metadata['Latitude'] = sublat
        combined_metadata['Longitude'] = sublon

        combined_metadata['Latitude_Metadata'] = sublat_meta
        combined_metadata['Longitude_Metadata'] = sublon_meta

        mode = getImageType(data)

        if mode in (1,2):
            combined_metadata['y_size'] = data.shape[0]
            combined_metadata['x_size'] = data.shape[1]
        else:
            combined_metadata['y_size'] = data.shape[1]
            combined_metadata['x_size'] = data.shape[2]


        # Store metadata filename for this product
        filename = os.path.split(modis_location)[-1]
        metadata_dict[filename] = combined_metadata

        # If not using a grid, store results
        if grid == None:
            data_dict[filename] = data

        # We are going to grid the data into smaller chunks
        else:
            # Get grid size
            y_grid = grid[0]
            x_grid = grid[1]

            y_size = data.shape[0]
            x_size = data.shape[1]

            # Determine number of grids based on image size
            num_y_grids = np.ceil(y_size / y_grid).astype(np.int)
            num_x_grids = np.ceil(x_size / x_grid).astype(np.int)

            dtype = data.dtype

            if np.isnan(grid_fill) and \
               not dtype in (np.float128, np.float64, np.float32, np.float16 ):

                if y_size % y_grid != 0 or x_size % x_grid != 0:
                    dtype = np.float

            # Loop over grids saving results
            for y_id in range(0,num_y_grids): 
                for x_id in range(0,num_x_grids):
                    y_start = y_id * y_grid
                    y_end = (y_id+1) * y_grid

                    x_start = x_id * x_grid
                    x_end = (x_id+1) * x_grid

                    section = createGrid(data, y_start, y_end, x_start, x_end, y_grid, x_grid, dtype)[0]

                    label = filename + ': ' + str((y_id, x_id))
                    data_dict[label] = section.copy()
                    metadata_dict[label] = OrderedDict()
                    metadata_dict[label]['full'] = metadata_dict[filename]
                    metadata_dict[label]['y_start'] = y_start
                    metadata_dict[label]['y_end'] = y_end
                    metadata_dict[label]['x_start'] = x_start
                    metadata_dict[label]['x_end'] = x_end          
                    metadata_dict[label]['x_size'] = x_end - x_start
                    metadata_dict[label]['y_size'] = y_start - y_end

    return ImageWrapper(data_dict,meta_data=metadata_dict)
