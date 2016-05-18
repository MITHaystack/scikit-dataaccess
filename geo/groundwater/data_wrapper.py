# The MIT License (MIT)
# Copyright (c) 2015 Massachusetts Institute of Technology
#
# Authors: Victor Pankratius, Justin Li, Cody Rude
# This software is part of the NSF DIBBS Project "An Infrastructure for
# Computer Aided Discovery in Geoscience" (PI: V. Pankratius) and 
# NASA AIST Project "Computer-Aided Discovery of Earth Surface 
# Deformation Phenomena" (PI: V. Pankratius)
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


# """@package Groundwater DataWrapper
# Provides Data classes for Groundwater data for use in the Computer-Aided Discovery pipeline.
# """

# mithagi required Base,Utils imports
from skdaccess.framework.data_class import DataWrapperBase
# 3rd party package imports

       

class DataWrapper(DataWrapperBase):
    '''Wraps GroundWater Data'''
    def __init__(self, obj_wrap, meta_data):
        ''' 
        Creates Ground Water Data Wrapper

        @param obj_wrap: Groundwater data to wrap
        @param meta_data: Groundwater meta data
        '''

        super(DataWrapper, self).__init__(obj_wrap)
        self.meta_data = meta_data

    def info(self):
        ''' 
        Get the ground water metadata

        @return meta_data
        '''
        return self.meta_data

    def getIndices(self):
        '''
        Get the indices of the data

        @return (station_list, 'Water Depth')
        '''
        return (list(self.data.keys()), ['Water Depth'])

    def getIterator(self):
        ''' 
        Get an iterator to access the ground water data

        @return Iterator to the data (label, data, error)
        '''

        if  len(self.data) > 0:
            for station in self.data['Water Depth'].columns:
                yield 'Water Depth', self.data.loc['Water Depth',:,station], None

