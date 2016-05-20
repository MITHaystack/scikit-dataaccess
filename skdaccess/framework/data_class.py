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

"""@package DataClass
Provides base data classes inherited by the specific data fetchers
"""
            
class DataFetcherBase:
    '''
    Base class for all data fetchers
    '''
    def __init__(self, ap_paramList=[]):
        ''' 
        Initialize data fetcher with parameter list
        
        @param ap_paramList: List of parameters
        '''

        self.ap_paramList = ap_paramList
    
    def output(self):
        ''' Output data wrapper '''
        pass

    def perturb(self):
        '''choose other random value for all parameters'''
        for param in self.ap_paramList:
            param.perturb()
            
    def reset(self):
        '''set all parameters to initial value'''
        for param in self.ap_paramList:
            param.reset()

    def __str__(self):
        ''' Generate string description'''
        return str( [ str(item) for item in self.ap_paramList ] )
            
    def getMetadata(self):
        '''
        Return metadata about Data Fetcher

        @return metadata of object.
        '''
        return str(self)
        
        

class DataWrapperBase(object):
    ''' Base class for wrapping data for use in DiscoveryPipeline. '''
    
    def __init__(self, obj_wrap, run_id = -1, meta_data = None):
        '''
        Construct object from input data. 

        @param obj_wrap: Data to be wrapped
        @param run_id: ID of the run
        '''
        self.data = obj_wrap
        self.results = dict()
        self.constants = dict()
        self.run_id = run_id
        self.meta_data = meta_data
    
    def update(self, obj):
        ''' Updated wrapped data '''
        self.data = obj
        
    def get(self):
        '''
        Retrieve stored data.

        @return Stored data
        '''
        return self.data
    
    def getResults(self):
        '''
        Retrieve accumulated results, if any.
        @return store results
        '''
        return self.results
        
    def addResult(self,rkey,rres):
        '''
        Passes a result to the data wrapper to be stored
        '''
        self.results[rkey] = rres
    
    def reset(self):
        ''' Reset data back to original state '''
        self.results = dict()

    def getIterator(self):
        ''' Get an iterator to the data '''
        pass

    def getIndices(self):
        ''' Get indices of the data '''
        pass

    def getLength(self):
        pass

class TableFetcher(DataFetcherBase):

    def __init__(self, pd_data):

        super(TableFetcher, self).__init__([])
        self.pd_data = pd_data


    def output(self):
        return DataPanelWrapper(self.pd_data)


class DataPanelWrapper(DataWrapperBase):
    '''
    Generic Data wrapper for pandas data panels. Iterators over data frames
    '''
    
    def getIterator(self):
        '''
        Iterator access to data. Iterates over the minor axis.

        @return iterator to data frames from Panel
        '''
        for label in self.data.minor_axis:
            yield label, self.data[:,:,label]

    def getLength(self):
        '''
        @return Number of data frames
        '''
        return len(self.data.minor_axis)
            

class DictionaryWrapper(DataWrapperBase):
    '''
    Generic data wrapper for a dictionary of data frames
    '''
    
    def getIterator(self):
        '''
        Iterator access to data. Iterates over the minor axis.

        @return iterator to data frames from Panel
        '''        
        for label in self.data.keys():
            yield label, self.data[label]


    def getLength(self):
        '''
        @return Number of data frames
        '''
        return len(self.data)
