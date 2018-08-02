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

# Standard library imports
from collections import OrderedDict
from html.parser import HTMLParser
from io import StringIO
import re
from calendar import monthrange


# 3rd party imports
import pandas as pd
from six.moves.urllib.parse import urlencode

# Package imports
from .support import convertToStr

class SoundingParser(HTMLParser):
    ''' This class parses Wyoming Sounding data '''
    def __init__(self):
        ''' Initialize SoundingParser '''

        self.data_dict = OrderedDict()
        self.metadata_dict = OrderedDict()
        self.label = None
        self.in_pre_tag = False
        self.in_header = False
        self.read_data = True

        super(SoundingParser, self).__init__()

    def handle_starttag(self, tag, attrs):
        '''
        Function called everytime a start tag is encountered

        @param tag: Starting tag
        @param attrs: Tag attributes
        '''
        if tag == 'pre':
            self.in_pre_tag = True

        elif re.match('h[0-9]*', tag):
            self.in_header = True

    def handle_endtag(self, tag):
        '''
        Function called everytime an end tag is encountered

        @param tag: Ending tag
        '''
        if tag == 'pre':
            self.in_pre_tag = False

        elif re.match('h[0-9]*', tag):
            self.in_header = False

    def handle_data(self, data):
        '''
        Function to parse data between \<pre\> tags

        @param data: Input data
        '''
        if self.in_pre_tag == True and self.read_data == True:
            self.data_dict[self.label] = pd.read_fwf(StringIO(data), widths=[7,7,7,7,7,7,7,7,7,7,7],
                                                     header=0, skiprows=[0,1,3,4])

            split_data = data.split('\n')
            headings = split_data[2].split()
            units = split_data[3].split()

            self.metadata_dict[self.label] = OrderedDict()
            self.metadata_dict[self.label]['units'] = [(heading, unit) for heading, unit in zip(headings, units)]
            self.read_data = False

            self.tmp = data

        elif self.in_pre_tag == True and self.read_data == False:


            station_metadata_dict = OrderedDict()
            for line in data.splitlines():
                if line != '':
                    metadata = line.split(':')
                    station_metadata_dict[metadata[0].strip()] = metadata[1].strip()

            self.metadata_dict[self.label]['metadata'] = station_metadata_dict
            self.read_data = True

        elif self.read_data == True and self.in_header == True:
            self.label = data.strip()


def generateQueries(station_number, year_list, month_list, day_start, day_end, start_hour,
                    end_hour):

    '''
    Generate url queries for sounding data

    @param station_number: Input station number
    @param year_list: Input years as a list
    @param month_list: Input month as a list
    @param day_start: Starting day
    @param day_end: Ending day
    @param start_hour: Starting hour
    @param end_hour: Ending hour

    @return list of urls containing requested data
    '''

    url_query_list = []
    base_url = 'http://weather.uwyo.edu/cgi-bin/sounding?'

    for year in year_list:
        for month in month_list:
            day_start = min(day_start, monthrange(year, month)[1])
            day_end = min(day_end, monthrange(year, month)[1])


            start_time = convertToStr(day_start,2) + convertToStr(start_hour,2)
            end_time = convertToStr(day_end,2) + convertToStr(end_hour,2)

            query = OrderedDict()
            query['region'] = 'naconf'
            query['TYPE'] = 'TEXT:LIST'
            query['YEAR'] = convertToStr(year, 0)
            query['MONTH'] = convertToStr(month, 2)
            query['FROM'] = start_time
            query['TO'] = end_time
            query['STNM'] = convertToStr(station_number, 5)

            url_query_list.append(base_url + urlencode(query))

    return url_query_list
