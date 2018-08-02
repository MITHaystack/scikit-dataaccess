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
from skdaccess.framework.data_class import DataFetcherStream, TableWrapper

# Standard library imports
from collections import OrderedDict
import os

# 3rd party imports
import pandas as pd
from geomagio.edge import EdgeFactory
from obspy.core import UTCDateTime
from pkg_resources import resource_filename


class DataFetcher(DataFetcherStream):
    ''' Data fetcher for USGS geomagnetic observatories '''
    def __init__(self, ap_paramList, start_time, end_time, interval = 'minute', 
                 channels=('X','Y','Z','F'), data_type = 'variation'):
        '''
        Geomagnetism Data fetcher constructor
        
        @param ap_paramList[AutoList]: AutoList of Observatory names
        @param start_time: Starting time
        @param end_time: Ending time
        @param interval: Time resolution
        @param channels: Data channels
        @param data_type = Data type
        '''
        
        self.start_time = start_time
        self.end_time = end_time
        self.interval = interval
        self.channels = channels
        self.data_type = data_type
        
        super(DataFetcher,self).__init__(ap_paramList)
        
    def output(self):
        ''' 
        Generate data wrapper for USGS geomagnetic data

        @return geomagnetic data wrapper
        '''
        
        observatory_list = self.ap_paramList[0]()
        
        # USGS Edge server
        base_url = 'cwbpub.cr.usgs.gov'     
        factory = EdgeFactory(host=base_url, port=2060)

        data_dict = OrderedDict()
        for observatory in observatory_list:
            ret_data = factory.get_timeseries( observatory=observatory,
                                               interval=self.interval,
                                               type=self.data_type,
                                               channels=self.channels,
                                               starttime=UTCDateTime(self.start_time),
                                               endtime=UTCDateTime(self.end_time))

            obs_data = OrderedDict()
            for label, trace in zip(self.channels, ret_data):
                time = pd.to_datetime(trace.stats['starttime'].datetime) + pd.to_timedelta(trace.times(),unit='s')
                obs_data[label] = pd.Series(trace.data,time)
                
            
            data_dict[observatory] = pd.DataFrame(obs_data)
            
                
        return TableWrapper(data_dict, default_columns=self.channels)

    

    def getDataMetadata():
        '''
        Get data metadata

        @return Pandas dataframe containing station latitude and 
                longitude coordinates
        '''

        meta_data_path = resource_filename('skdaccess',os.path.join('support','usgs_geomagnetism_observatories.txt'))
        return pd.read_csv(meta_data_path, header=None, names=('Observatory','Lat','Lon')).set_index('Observatory')
