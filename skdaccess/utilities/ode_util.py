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
from xml.dom import minidom
from six.moves.urllib.request import urlopen
from osgeo import gdal

# Standard library imports
from collections import OrderedDict
import sys
import re

def query_yes_no(question, default = "yes"):
    '''
    Ask a yes/no question via raw_input() and return the answer
    Written by Trent Mick under the MIT license, see:
    https://code.activestate.com/recipes/577058-query-yesno/
    
    @param question: A string that is presented to the user
    @param default: The presumed answer if the user just hits <Enter>.
                    It must be "yes" (the default), "no" or None (meaning
                    an answer is required of the user)

    @return The "answer", i.e., either "yes" or "no"
    '''
    
    valid = {"yes":"yes",   "y":"yes",  "ye":"yes",
             "no":"no",     "n":"no"}
    if default == None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while 1:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return default
        elif choice in valid.keys():
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "\
                             "(or 'y' or 'n').\n")

def get_query_url(target, mission, instrument, product_type,
                  western_lon, eastern_lon, min_lat, max_lat,
                  min_ob_time, max_ob_time, product_id,
                  query_type, output, results,
                  number_product_limit, result_offset_number):
    '''
    Build the query URL using ODE REST interface
    Adapted from the Orbital Data Explorer (ODE) REST Interface Manual
    
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
    @param product_id: PDS Product Id to look for, with wildcards (*) allowed
    @param query_type: File type to look for, i.e., Product, Browse, Derived, or Referenced
    @param output: Return format for product queries or error messages, i.e, XML or JSON
    @param results: Type of files to look for, i.e., c: count of products; o: ODE Product ID;
                    p: PDS product identifies; m: product metadata; f: product files; b: browse image;
                    t: thumbnail image; l: complete PDS label; x: single product footprint
    @param number_product_limit: Maximal number of products to return (100 at most)
    @param result_offset_number: Offset the return products, to go beyond the limit of 100 returned products
    
    @return Query URL
    '''

    ODE_REST_base_url = "http://oderest.rsl.wustl.edu/live2/?"

    target = 'target=' + target
    mission = '&ihid=' + mission
    instrument = '&iid=' + instrument
    product_type = '&pt=' + product_type
    if western_lon is not None: 
        western_lon = '&westernlon=' + str(western_lon)
    else:
        western_lon = ''
    if eastern_lon is not None: 
        eastern_lon = '&easternlon=' + str(eastern_lon)
    else:
        eastern_lon = ''
    if min_lat is not None: 
        min_lat = '&minlat=' + str(min_lat)
    else:
        min_lat = ''
    if max_lat is not None: 
        max_lat = '&maxlat=' + str(max_lat)
    else:
        max_lat = ''
    if min_ob_time != '': 
        min_ob_time = '&mincreationtime=' + min_ob_time
    if max_ob_time != '': 
        max_ob_time = '&maxcreationtime=' + max_ob_time
    if product_id != '':
        product_id = '&productid=' + product_id

    if query_type != '': 
        query_type = '&query=' + query_type
    if results != '': 
        results = '&results=' + results
    if output != '': 
        output = '&output=' + output
    if number_product_limit != '': 
        number_product_limit = '&limit=' + str(number_product_limit)
    if result_offset_number != '': 
        result_offset_number = '&offset=' + str(result_offset_number)

    # Concatenate the REST request
    return ODE_REST_base_url + target + mission + instrument + product_type \
           + western_lon + eastern_lon + min_lat + max_lat + min_ob_time \
           + max_ob_time + query_type + results + output + number_product_limit \
           + result_offset_number + product_id
            
def get_files_urls(query_url, file_name = '*', print_info = False):
    '''
    Retrieve the files' URLs based on a query from ODE REST interface
    Adapted from the Orbital Data Explorer (ODE) REST Interface Manual
    
    @param query_url: URL resulting from the query of ODE
    @param file_name: File name to look for, with wildcards (*) allowed
    @param print_info: Print the files that will be downloaded
    
    @return List of URLs
    '''
    
    url = urlopen(query_url)
    query_results = url.read()
    xml_results = minidom.parseString(query_results)
    url.close()
    
    error = xml_results.getElementsByTagName('Error')
    if len(error) > 0:
        print('\nError:', error[0].firstChild.data)
        return None
    
    limit_file_types = 'Product'
    file_name = file_name.replace('*', '.')
    
    products = xml_results.getElementsByTagName('Product')
    file_urls = OrderedDict()
    for product in products:
        product_files = product.getElementsByTagName('Product_file')
        product_id = product.getElementsByTagName('pdsid')[0]
        if print_info == True:
            print('\nProduct ID:', product_id.firstChild.data)
        for product_file in product_files:
            file_type = product_file.getElementsByTagName('Type')[0]
            file_url = product_file.getElementsByTagName('URL')[0]
            file_description = product_file.getElementsByTagName('Description')[0]
            local_filename = file_url.firstChild.data.split('/')[-1]
            local_file_extension = local_filename.split('.')[-1]
            if re.search(file_name, local_filename) is not None:
                # Restriction on the file type to download
                if len(limit_file_types) > 0:
                    # If match, get the URL
                    if file_type.firstChild.data == limit_file_types:
                        file_urls[file_url.firstChild.data] = (product_id.firstChild.data,
                                                               file_description.firstChild.data)
                        if print_info == True:
                            print('File name:', file_url.firstChild.data.split('/')[-1])
                            print('Description:', file_description.firstChild.data)
                # No restriction on the file type to download
                else:
                    file_urls[file_url.firstChild.data] = (product_id.firstChild.data,
                                                           file_description.firstChild.data)
                    if print_info == True:
                        print('File name:', file_url.firstChild.data.split('/')[-1])
                        print('Description:', file_description.firstChild.data)

    return file_urls

def query_files_urls(target, mission, instrument, product_type,
                     western_lon, eastern_lon, min_lat, max_lat,
                     min_ob_time, max_ob_time, product_id, file_name,
                     number_product_limit, result_offset_number):
    '''
    Retrieve the URL locations based on a query using ODE REST interface
    
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
    @param product_id: PDS Product Id to look for, with wildcards (*) allowed
    @param file_name: File name to look for, with wildcards (*) allowed
    @param number_product_limit: Maximal number of products to return (100 at most)
    @param result_offset_number: Offset the return products, to go beyond the limit of 100 returned products
    
    @return List of URL locations
    '''
    
    # Returns a list of products with selected product metadata that meet the query parameters
    query_type = 'product'
    # Controls the return format for product queries or error messages
    output = 'XML'
    # For each product found return the product files and IDS
    results = 'fp'

    query_url = get_query_url(target, mission, instrument, product_type,
                              western_lon, eastern_lon, min_lat, max_lat,
                              min_ob_time, max_ob_time, product_id,
                              query_type, output, results,
                              number_product_limit, result_offset_number)
                
    print('Query URL:', query_url)
    print('\nFiles that will be downloaded (if not previously downloaded):')
    file_urls = get_files_urls(query_url, file_name, print_info = True)
    if file_urls is None:
        return OrderedDict()
    elif len(file_urls) > 0:
        should_continue = query_yes_no('\nDo you want to proceed?')
        if should_continue == "no":
            return OrderedDict()
    else:
        print('\nNo file found')
    
    return file_urls

def correct_CRISM_label(label_file_location):
    '''
    Correct CRISM label file and allow GDAL to read it properly.
    Necessary for Targeted Reduced Data Record (TRDR) data
    Adapted from https://github.com/jlaura/crism/blob/master/csas.py
    
    @param label_file_location: Local address of the current label
    
    @return Local address of the new label
    '''
    
    new_label_file_location = label_file_location
    if '_fixed' not in new_label_file_location:
        new_label_file_location = '.'.join(label_file_location.split('.')[:-1]) \
                                  + '_fixed.' + label_file_location.split('.')[-1]
    new_label_file = open(new_label_file_location, 'w')
    
    for line in open(label_file_location, 'r'):
        if "OBJECT          = FILE" in line:
            line = "/* OBJECT = FILE */\n"
        if "LINES" in line:
            lines = int(line.split("=")[1])
        if "LINE_SAMPLES" in line:
            samples = int(line.split("=")[1])
        new_label_file.write(line)
        
    new_label_file.close()

    return new_label_file_location

def correct_file_name_case_in_label(label_file_location, other_file_locations):
    '''
    Correct a label file if the case of the related data file(s) is incorrect
    and GDAL cannot read it properly
    
    @param label_file_location: Local address of the current label
    @param other_file_locations: Other files that were downloaded with the label file
    
    @return Local address of the new label
    '''
    
    label_file_name = '_'.join('.'.join(label_file_location.split('/')[-1].split('.')[:-1]).split('_')[:-1])
    insensitive_lalels = []
    for file_location in other_file_locations:
        file_name = '.'.join(file_location.split('/')[-1].split('.')[:-1])
        if (file_location != label_file_location
            and file_name == label_file_name):
                insensitive_lalel = re.compile(re.escape(file_location.split('/')[-1]),
                                               re.IGNORECASE)
                insensitive_lalels.append((insensitive_lalel,
                                           file_location.split('/')[-1]))
    
    with open(label_file_location, 'r') as file:
        label_file = file.read()
        
    for insensitive_lalel, sensitive_lalel in insensitive_lalels:
        label_file = insensitive_lalel.sub(sensitive_lalel, label_file)

    new_label_file_location = label_file_location
    if '_fixed' not in new_label_file_location:
        new_label_file_location = '.'.join(label_file_location.split('.')[:-1]) \
                                  + '_fixed.' + label_file_location.split('.')[-1]
    with open(new_label_file_location, 'w') as file:
        file.write(label_file)

    return new_label_file_location

def correct_label_file(label_file_location, other_file_locations = []):
    '''
    Correct a label file if GDAL cannot open the corresponding data file
    
    @param label_file_location: Local address of the current label
    @param other_file_locations: Other files that were downloaded with the label file
    
    @return Local address of the new label
    '''
    
    # Correction not limited to CRISM data, in case other data had similar issues
    new_label_file_location = correct_CRISM_label(label_file_location)
    return correct_file_name_case_in_label(new_label_file_location,
                                           other_file_locations)

def get_raster_array(gdal_raster, remove_ndv = True):
    '''
    Get a NumPy array from a raster opened with GDAL
    
    @param gdal_raster: A raster opened with GDAL
    @param remove_ndv: Replace the no-data value as mentionned in the label by np.nan
    
    @return The array
    '''
    assert gdal_raster is not None, 'No raster available'
    
    number_of_bands = gdal_raster.RasterCount
    raster_array = gdal_raster.ReadAsArray().astype(np.float)
    for i_band in range(number_of_bands):
        raster_band = gdal_raster.GetRasterBand(i_band + 1)
        no_data_value = raster_band.GetNoDataValue()
        if no_data_value is not None and remove_ndv == True:
            if number_of_bands > 1:
                raster_array[i_band, :, :][raster_array[i_band, :, :] == no_data_value] = np.nan
            else:
                raster_array[raster_array == no_data_value] = np.nan
        scale = raster_band.GetScale()
        if scale is None:
            scale = 1.
        offset = raster_band.GetOffset()
        if offset is None:
            offset = 0.
        if number_of_bands > 1:
            raster_array[i_band, :, :] = raster_array[i_band, :, :]*scale + offset
        else:
            raster_array = raster_array*scale + offset
            
    return raster_array

def get_raster_extent(gdal_raster):
    '''
    Get the extent of a raster opened with GDAL
    
    @param gdal_raster: A raster opened with GDAL
    
    @return The raster extent
    '''
    assert gdal_raster is not None, 'No raster available'
    
    raster_x_size = gdal_raster.RasterXSize
    raster_y_size = gdal_raster.RasterYSize
    geotransform = gdal_raster.GetGeoTransform()
    xmin = geotransform[0]
    ymax = geotransform[3]
    xmax = xmin + geotransform[1]*raster_x_size
    ymin = ymax + geotransform[5]*raster_y_size
    
    return (xmin, xmax, ymin, ymax)
    