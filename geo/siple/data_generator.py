# The MIT License (MIT)
# Copyright (c) 2016 Massachusetts Institute of Technology
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

"""@package Stanford University Siple VLF DataGenerator
Provides Data classes for  Stanford University Siple VLF data for use in the Computer-Aided Discovery pipeline.
"""

# mithagi required Base imports
from skdaccess.framework.data_class import DataGeneratorBase
from skdaccess.utilities.data_util import getDataLocation
from skdaccess.geo.siple.data_wrapper import DataWrapper

# 3rd party package imports
import pandas as pd
import numpy as np
import tables
import glob.glob as glob


class DataGenerator(DataGeneratorBase):
    '''
    Generates Data Wrappers of VLF data collected by Stanford University VLF Group at Siple Station, Antarctica in 1986 (for now)
    '''
    def __init__(self,  ap_paramList = [], start_datestamp = None, end_datestamp = None, data_duration = None):
        ''' 
        Construct a VLF Data Generator

        @param ap_paramList[file_name]: complete file name, including extension (Optional)
        @param start_datestamp: Starting date/time as MM-DD HH:MM:SS (defualt: None)
        @param end_datestamp: Ending date/time as HH:MM:SS (default: None)
        @param data_duration: Data duration in seconds (default: None)
        '''
        
        if self.ap_paramList == []:
            file_name = self.ap_paramList[0]()
        else:
            pfilesn = glob('sLM1986'+start_datestamp[0:2]+start_datestamp[3:5])
            if len(pfilsn) == 0:
                print('No Data Available for this Day')
                file_name = None
            elif len(pfilsn)>1:
                possibleH = np.array([int(apfn[0:2]) for apfn in pfilesn])
                possibleH -= int(start_datestamp[6:8])
                file_name = pfilsn[np.argmax(possibleH[possibleH<0])]
            elif len(pfilsn)==1:
                file_name = pfilesn[0]
            
        mfile = tables.open_file('../Desktop/Stanford_Siple/py1986_data/'+file_name,mode='r')
        ddata = mfile.get_node('/data') # the entire data node
        nchan = mfile.get_node('/nchan').read()[0][0] # number of channels
        fs = int(mfile.get_node('/fs').read()[0][0]) # sampling frequency
        
        tstart = datetime.datetime(1986,int(start_datestamp[0:2]),int(start_datestamp[3:5]),
                                   int(start_datestamp[6:8]),int(start_datestamp[9:11]),
                                   int(start_datestamp[12:14]))
                                   
        tstart = datetime.datetime(1986,int(start_datestamp[0:2]),int(start_datestamp[3:5]),
                                   int(start_datestamp[6:8]),int(start_datestamp[9:11]),
                                   int(start_datestamp[12:14]))

        if end_datestamp != None:
            # determine length by ending date/time stamp
        elif data_duration != None:
            # otherwise use the data duration parameter
        else:
            # or default to 1 minute
ts = 32; te=32.5
data = ddata[0,ts*60*fs:te*60*fs]         
        
        self.meta_data = DataGenerator.getStationMetadata()

        self.start_date   = pd.to_datetime(start_date)
        self.end_date     = pd.to_datetime(end_date)
        self.ap_paramList = ap_paramList
        self.cutoff = cutoff
        self.adjust_heights = adjust_heights

    def output(self):
        ''' 
        Generate Groundwater Data Wrapper

        @return Groundwater Data Wrapper
        '''

        data_file    = getDataLocation('groundwater')
        if data_file is None:
            print("No data available")
            return None


        if self.ap_paramList == []:
            station_list = []
        else:
            station_list = self.ap_paramList[0]()



        data_dict = dict()
        store = pd.HDFStore(data_file, 'r')

        if station_list == []:
            stations = [station[5:] for station in store.keys() if station != '/meta_data']

        else:
            stations = station_list

        for station in stations:
            if self.start_date != None and self.end_date != None:
                data = store['USGS' + str(station)].reindex(pd.date_range(self.start_date, self.end_date))
            else:
                data = store['USGS' + str(station)]
            if len(data.dropna()) / len(data) > self.cutoff:
                if self.adjust_heights == False:
                    data_dict[str(station)] = data
                else:
                    altitude = self.meta_data.loc[int(station), 'Altitude']
                    # altitude_unc = self.meta_data.loc[int(station), 'AltitudeAccuracy']
                    data.loc[:, 'Water Depth'] = altitude - data.loc[:, 'Water Depth']
                    # data.loc[:, 'Uncertainty'] = data.loc[:,'Uncertainty']
                    data_dict[str(station)] = data
                
        store.close()

        data = DataWrapper(pd.Panel.from_dict(data_dict,orient='minor'), self.meta_data)
        return data

    def __str__(self):
        '''
        String representation of data generator

        @return string describing data generator
        '''
        return 'Ground Water Data Generator' + super(DataGenerator, self).__str__()


    def getStationMetadata():
        data_file = getDataLocation('groundwater')
        if data_file is None:
            print('Dataset not available')
            return None

        store = pd.HDFStore(data_file,'r')
        meta_data = store['meta_data']
        store.close()
        
        return meta_data
