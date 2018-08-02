# The MIT License (MIT)
# Copyright (c) 2018 Massachusetts Institute of Technology
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


# Standard library imports
import xml.etree.ElementTree as ET

# 3rd party imports
import pandas as pd

def parseSatelliteData(in_satellite_file):
    '''
    Parse Sentinel satelllite data

    @param in_satellite_file: Satellite orbit filename

    @return DataFrame of orbit information
    '''
    satellite_tree = ET.parse(in_satellite_file)

    names = ['TAI', 'UTC', 'UT1','Absolute_Orbit', 'X', 'Y', 'Z', 'VX', 'VY', 'VZ', 'Quality']
    time_converter = lambda x: pd.to_datetime(x[4:])
    converters = [time_converter, time_converter, time_converter, int, float, float, float,
                  float, float, float, lambda x: x]
    tmp_data = []

    for orbit in satellite_tree.findall('Data_Block/List_of_OSVs/OSV'):
        row = []
        for name, converter in zip(names, converters):
            row.append(converter(orbit.find(name).text))
        tmp_data.append(row)

    return pd.DataFrame(tmp_data, columns=names)
