# The MIT License (MIT)
# Copyright (c) 2016 Massachusetts Institute of Technology
#
# Authors: Victor Pankratius, Justin Li, Cody Rude#
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

"""@package PBO
Provides classes for accessing PBO data.
"""

# mithagi required Base,Utils imports
from skdaccess.framework.data_class import DataFetcherBase, DataPanelWrapper
from skdaccess.utilities import pbo_util
from skdaccess.utilities import data_util

#IGNORE THIS LINE
from skdaccess.geo.pbo.data_wrapper import DataWrapper

# 3rd party package imports
import pandas as pd
import numpy as np



class DataFetcher(DataFetcherBase):
    ''' data_type = "pbo" or "snow" for now
        the parameters list must include:
        1) region of interest window (for generating stations list)
        2) stabilization area (for running stabilization)
    '''
    
    def __init__(self, start_time, end_time, lat_range, lon_range, ap_paramList, mdyratio=.5, ep_flag=1, stab_flag=1, wrapper_type='series'):
        ''' 
        Initialize a DataFetcher

        @param start_time: String of starting date in the form of "2005-01-01"
        @param end_time: String of ending date in the form of "2014-12-31"
        @param lat_range: Latitude range used to select stabilization sites
        @param lon_range: Longitude range used to select stabilization sites
        @range ap_paramList[radius]: Site radius to search around (km)
        @param ap_paramList[geo_point] Tuple containing lat and lon coordinates
        @param ep_flag: Propagate errors through stabilization
        @param stab_flag: Perform regional stabilization
        @param wrapper_type: Select the type of iterator wrapper to generate, as series or table
        '''
        
        
        self._start_time = start_time
        self._end_time = end_time
        self.ap_paramList = ap_paramList
        self._geospace = (lat_range, lon_range)
        self.station_list = None
        self._mdyratio = mdyratio
        self._ep_flag = ep_flag
        self._stab_flag = stab_flag
        self.wrapper_type = wrapper_type

        self.meta_data = DataFetcher.getStationMetadata()

        if stab_flag == 1:
            self.stabilize()
        else:
            self.rawData()

    def setStationList(self, station_list):
        self.station_list = station_list
        
    def stationCheck(self):
        '''
        Generates a list of stations within site radius

        @return List of stations within site radius
        '''

        geo_point = (self.ap_paramList[1]()[0], self.ap_paramList[1]()[1])

        radiusParam = self.ap_paramList[0]()
        
        # checks if enough stations in vicinity
        storeName = self.meta_data
        radiusParam = self.ap_paramList[0].val
        # finds the station list
        ccPos = (geo_point[0]*np.pi/180, geo_point[1]*np.pi/180)
        station_list = []
        for ii in storeName.keys():
            coord = (storeName[ii]['refNEU'][0]*np.pi/180,(storeName[ii]['refNEU'][1]-360)*np.pi/180)
            dist = 6371*2*np.arcsin(np.sqrt(np.sin((ccPos[0]-coord[0])/2)**2+np.cos(ccPos[0])*np.cos(coord[0])*np.sin((ccPos[1]-coord[1])/2)**2))
            if np.abs(dist) < radiusParam:
                station_list.append(storeName[ii]['4ID'])
        return station_list
    
    
    def stabilize(self):
        ''' 
        Select data from sites within site radius for later use in stabilization.
        '''
        
        storeName = self.meta_data

        storeData_fn = data_util.getDataLocation('pbo')
        if storeData_fn is None:
            print('Dataset not available')
            return None

        storeData = pd.HDFStore(storeData_fn)

        mdyratio = self._mdyratio
        epFlag = self._ep_flag

        keyList =[]
        for ii in storeName.keys():
            coord = storeName[ii]['refNEU']
            if coord[0]>self._geospace[0][0] and coord[0]<self._geospace[0][1] and coord[1]>self._geospace[1][0] and coord[1]<self._geospace[1][1]:
                keyList.append(storeName[ii]['4ID'])
            elif coord[0]>self._geospace[0][0] and coord[0]<self._geospace[0][1] and coord[1]>(360+self._geospace[1][0]) and coord[1]<(360+self._geospace[1][1]):
                keyList.append(storeName[ii]['4ID'])
        smSet_all, smHdr_all = pbo_util.stab_sys(storeName,storeData,[self._start_time,self._end_time],indx=keyList,mdyratio=mdyratio,errProp=epFlag)

        self.smSet_all = smSet_all
        self.smHdr_all = smHdr_all
        storeData.close()


    def rawData(self):
        ''' 
        Select data from sites within site radius to be returned without stabilization.
        '''
        
        storeName = self.meta_data

        storeData_fn = data_util.getDataLocation('pbo')
        if storeData_fn is None:
            print('Dataset not available')
            return None

        storeData = pd.HDFStore(storeData_fn)

        mdyratio = self._mdyratio

        keyList =[]
        for ii in storeName.keys():
            coord = storeName[ii]['refNEU']
            if coord[0]>self._geospace[0][0] and coord[0]<self._geospace[0][1] and coord[1]>self._geospace[1][0] and coord[1]<self._geospace[1][1]:
                keyList.append(storeName[ii]['4ID'])
            elif coord[0]>self._geospace[0][0] and coord[0]<self._geospace[0][1] and coord[1]>(360+self._geospace[1][0]) and coord[1]<(360+self._geospace[1][1]):
                keyList.append(storeName[ii]['4ID'])
        smSet_all, smHdr_all = pbo_util.nostab_sys(storeName,storeData,[self._start_time,self._end_time],indx=keyList,mdyratio=mdyratio)

        self.smSet_all = smSet_all
        self.smHdr_all = smHdr_all
        storeData.close()
        

    def getInfo(self):

        storeName = self.meta_data

        if self.station_list == None and len(self.ap_paramList) > 0:

            geo_point = (self.ap_paramList[1]()[0], self.ap_paramList[1]()[1])

            radiusParam = self.ap_paramList[0]()

            ccPos = (geo_point[0]*np.pi/180, geo_point[1]*np.pi/180)
            
            station_list = []
            for ii in self.smHdr_all.keys():
                coord = (storeName[ii]['refNEU'][0]*np.pi/180,(storeName[ii]['refNEU'][1]-360)*np.pi/180)
                dist = 6371*2*np.arcsin(np.sqrt(np.sin((ccPos[0]-coord[0])/2)**2+np.cos(ccPos[0])*np.cos(coord[0])*np.sin((ccPos[1]-coord[1])/2)**2))
                if np.abs(dist) < radiusParam:
                    station_list.append(storeName[ii]['4ID'])

        elif self.station_list == None:
            station_list = list(self.smHdr_all.keys())
            latlonrange = pbo_util.getLatLonRange(storeName, station_list)
            geo_point = (np.mean(latlonrange[0]), np.mean(latlonrange[1]))            
            

        else:
            station_list = self.station_list
            latlonrange = pbo_util.getLatLonRange(storeName, station_list)
            geo_point = (np.mean(latlonrange[0]), np.mean(latlonrange[1]))

        return station_list, geo_point
        

    def output(self):
        '''
        Generate PBO Data Wrapper

        @return PBO Data Wrapper
        '''

        station_list, geo_point = self.getInfo()

        # grabs the stabilized data for the desired stations
        data = dict(); info = dict();
        for ii in station_list:
            if ii in self.smHdr_all.keys():
                data[ii] = self.smSet_all[ii]
                info[ii] = self.smHdr_all[ii]

        if self.wrapper_type == 'series':
            return DataWrapper(pd.Panel.from_dict(data, orient='minor'), geo_point, info)
        elif self.wrapper_type == 'table':
            return(DataPanelWrapper(pd.Panel.from_dict(data,orient='minor'), meta_data=info))
        else:
            print('... Invald wrapper type, defaulting to series ...')
            return DataWrapper(pd.Panel.from_dict(data, orient='minor'), geo_point, info)


    def __str__(self):
        '''
        print the parameter values

        @return String representation of Data Fetcher
        '''
        return 'PBO Data Fetcher' + super(DataFetcher, self).__str__()

    def getStationMetadata():
        '''
        Read in the metadata and convert to dictionary

        @return dictionary of PBO metadata
        '''

        storeData_fn = data_util.getDataLocation('pbo')
        if storeData_fn is None:
            print('Dataset not available')
            return None

        store = pd.HDFStore(storeData_fn, 'r')
        meta_frame = store['meta_data']

        meta_data = dict()
        for site, data in meta_frame.iterrows():
            meta_data[site] = dict()
            meta_data[site]['refNEU'] = [data['N_ref'], data['E_ref'], data['U_ref']]
            meta_data[site]['refXYZ'] = [data['X_ref'], data['Y_ref'], data['Z_ref']]
            meta_data[site]['4ID'] = site


        store.close()

        return meta_data

    def getMetadata(self):
        station_list, geo_point = self.getInfo()
        return 'PBO Data Fetcher', geo_point, station_list
