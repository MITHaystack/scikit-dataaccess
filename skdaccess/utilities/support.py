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

# Standard library imports
from collections import OrderedDict
import os


# 3rd party import
import pandas as pd
from pkg_resources import resource_filename
from tqdm import tqdm


def retrieveCommonDatesHDF(support_data_filename, key_list, in_date_list):
    '''
    Get a list of all dates that have  data available

    @param support_data_filename: Filename of support data
    @param key_list: List of keys in HDF file
    @param in_date_list: Input date list to check

    @return dictionary of dates with data
    '''

    valid_dates = OrderedDict()

    support_full_path = resource_filename('skdaccess',os.path.join('support',support_data_filename))

    for key in key_list:

        try:
            available_dates = pd.read_hdf(support_full_path, key)
        except KeyError:
            print('Unknown station:',key)

        common_dates = list(set(in_date_list).intersection(set(available_dates)))

        common_dates.sort()

        valid_dates[key] = common_dates

    return valid_dates


def progress_bar(in_iterable, total=None, enabled=True):
    '''
    Progess bar using tqdm

    @param in_iterable: Input iterable
    @param total: Total number of elements
    @param enabled: Enable progress bar
    '''

    if enabled==True:
        return tqdm(in_iterable, total=total)
    else:
        return in_iterable

def convertToStr(in_value, zfill=0):
    '''
    If input is a number, convert to a string
    with zero paddding. Otherwise, just return
    the string.

    @input in_value: Input string or number
    @zfill: Amount of zero padding

    @return zero padded number as a string, or original string
    '''

    if isinstance(in_value, str):
        return in_value
    else:
        return str(in_value).zfill(zfill)

def join_string(part1, part2, concatenation_string = 'AND', seperator=' '):
    """
    Join two strings together using a concatenation string

    Handles the case where either part1 or part2 are an empty string

    @param part1: First string
    @param part2: Second string
    @param concatenation_string: String used to join part1 and part2
    @param seperator: Seperator used to between each part and the
                      concatenation string

    @return A single string that consists of the part1 and part2
            joined together using a concatenation string
    """

    if part1 == '':
        return part2

    elif part2 == '':
        return part1


    if part1[-1] == seperator:
        sep1 = ''
    else:
        sep1 = seperator


    if part2[0] == seperator:
        sep2 = ''
    else:
        sep2 = ' '


    return part1 + sep1 + concatenation_string + sep2 + part2
