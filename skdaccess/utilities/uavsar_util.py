# The MIT License (MIT)
# Copyright (c) 2017 Massachusetts Institute of Technology
#
# Author: Cody Rude
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

import re
from collections import OrderedDict

def readUAVSARMetadata(in_file):
    '''
    Parse UAVSAR metadata

    @param in_file: String of Metadata filename or file object (file should end in .ann)

    @return OrderedDict of metadata
    '''

    if isinstance(in_file, str):
        with open(in_file, 'r') as info_file:
            data_info = info_file.readlines()

    else:
        data_info = [line.decode() for line in in_file.readlines()]



    data_info = [line.strip() for line in data_info]


    # Function to convert string to a number
    def str_to_number(in_string):
        try:
            return int(in_string)
        except:
            return float(in_string)


    data_name = data_info[0][31:]


    meta_data_dict = OrderedDict()
    for line in data_info:
        # Only work on lines that aren't commented out
        if re.match('^[^;]',line) != None:
            # Get the data type ('&' is text)
            data_type = re.search('\s+\((.*)\)\s+=', line).group(1)
            # Remove data type from line
            tmp = re.sub('\s+\(.*\)\s+=', ' =', line)

            # Split line into key,value
            split_list = tmp.split('=',maxsplit=1)

            # remove any trailing comments and strip whitespace
            split_list[1] = re.search('[^;]*',split_list[1]).group().strip()
            split_list[0] = split_list[0].strip()

            #If data type is not a string, parse it as a float or int
            if data_type != '&':
                # Check if value is N/A
                if split_list[1] == 'N/A':
                    split_list[1] = float('nan')

                # Check for Raskew Doppler Near Mid Far as this
                # entry should be three seperate entries
                elif split_list[0] == 'Reskew Doppler Near Mid Far':
                    split_list[0] = 'Reskew Doppler Near'

                    second_split = split_list[1].split()
                    split_list[1] = str_to_number(second_split[0])

                    meta_data_dict['Reskew Doppler Mid'] = str_to_number(second_split[1])
                    meta_data_dict['Reskew Doppler Far'] = str_to_number(second_split[2])

                # Parse value to an int or float
                else:
                    split_list[1] = str_to_number(split_list[1])
            # Add key, value pair to dictionary
            meta_data_dict[split_list[0]] = split_list[1]

    return meta_data_dict
