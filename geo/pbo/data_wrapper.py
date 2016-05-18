# The MIT License (MIT)
# Copyright (c) 2016 Massachusetts Institute of Technology
#
# Authors: Victor Pankratius, Justin Li, Cody Rude
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

# """@package PBO DataWrapper
# Provides Data classes for PBO data for use in the Computer-Aided Discovery pipeline.
# """

# mithagi required Base,Utils imports
from skdaccess.framework.data_class import DataWrapperBase

# 3rd party package imports

       

class DataWrapper(DataWrapperBase):
    ''' Class used to wrap PBO Data '''
    def __init__(self, obj_wrap, geo_poi, info_dict):
        ''' 
        Initialize DataWrapper 

        @param obj_wrap: Data to be wrapped
        @param lp_stations: list perturber containing station list
        @param geo_poi: Geographic point of interenst
        '''
        super(DataWrapper, self).__init__(obj_wrap)
        self.geo_point = geo_poi
        self.info_dict = info_dict

    def info(self):
        '''
        Retrieve stored data metadata.

        @return Stored data metadata
        '''
        return self.info_dict
        
    def getIterator(self):
        ''' 
        Get an iterator to the data

        @return Iterator that will cycle over ('dN', 'dE', 'dU') for each station
        '''

        tp_directions = ('dN', 'dE', 'dU')
        tp_uncertainties = ('Sn', 'Se', 'Su')

        for station in self.data.iloc[0].columns:
            for direction,err in zip(tp_directions, tp_uncertainties):
                yield direction, self.data.loc[direction, :, station], self.data.loc[err, :, station]

    def getIndices(self):
        ''' 
        Get the indicies of the data
        
        @return (station_list, ('dN', 'dE', 'dU'))
        '''
        
        return (list(self.data.iloc[0].columns), ('dN', 'dE', 'dU'))
