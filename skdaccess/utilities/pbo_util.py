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

# """@package pbo_util
# Tools for working with PBO GPS data, including reference frame stabilization code
# """


import numpy as np
import pandas as pd
import warnings
from datetime import datetime
from .support import progress_bar

def getStationCoords( pbo_info, station_list):
    '''
    Get the station coordinates for a list of stations

    @param pbo_info: PBO Metadata
    @param station_list: List of stations

    @return list of tuples containing lat, lon coordinates of stations
    '''

    coord_list = []

    for station in station_list:
        lat = pbo_info[station]['refNEU'][0]
        lon = pbo_info[station]['refNEU'][1]-360

        coord_list.append( (lat,lon))


    return coord_list


def getLatLonRange(pbo_info, station_list):
    '''
    Retrive the range of latitude and longitude occupied by a set of stations

    @param pbo_info: PBO Metadata
    @param station_list: List of stations

    @return list containg two tuples, lat_range and lon_range
    '''

    coord_list = getStationCoords(pbo_info, station_list)

    lat_list = []
    lon_list = []
    for coord in coord_list:
        lat_list.append(coord[0])
        lon_list.append(coord[1])

    lat_range = (np.min(lat_list), np.max(lat_list))
    lon_range = (np.min(lon_list), np.max(lon_list))

    return [lat_range, lon_range]


def getROIstations(geo_point,radiusParam,data,header):
    '''
    This function returns the 4ID station codes for the stations in a region

    The region of interest is defined by the geographic coordinate and a window size

    @param geo_point: The geographic (lat,lon) coordinate of interest
    @param radiusParam: An overloaded radius of interest [km] or latitude and longitude window [deg] around the geo_point
    @param data: Stabilized (or unstabilized) data generated from the data fetcher or out of stab_sys
    @param header: Header dictionary with stations metadata keyed by their 4ID code. This is output with the data.
    
    @return station_list, list of site 4ID codes in the specified geographic region
     '''
    ccPos = (geo_point[0]*np.pi/180, geo_point[1]*np.pi/180)
    if np.isscalar(radiusParam):
        station_list = []
        for ii in header.keys():
            coord = (header[ii]['refNEU'][0]*np.pi/180,(header[ii]['refNEU'][1]-360)*np.pi/180)
            dist = 6371*2*np.arcsin(np.sqrt(np.sin((ccPos[0]-coord[0])/2)**2+np.cos(ccPos[0])*np.cos(coord[0])*np.sin((ccPos[1]-coord[1])/2)**2))
            if np.abs(dist) < radiusParam:
                station_list.append(header[ii]['4ID'])
    else:
        # overloaded radiusParam term to be radius or lat/lon window size
        latWin = radiusParam[0]/2
        lonWin = radiusParam[1]/2
        station_list = []

        try:
            for ii in header.keys():
                coord = (header[ii]['refNEU'][0],(header[ii]['refNEU'][1]-360))
                if (geo_point[0]-latWin)<=coord[0]<=(geo_point[0]+latWin) and (geo_point[1]-lonWin)<=coord[1]<=(geo_point[1]+lonWin):
                    station_list.append(header[ii]['4ID'])
        except:
            station_list = None
            
    return station_list


def stab_sys(data_iterator,metadata,stab_min_NE=.0005,stab_min_U=.005,sigsc=2,
             errProp=1):
    '''
    Stabilize GPS data to a region

    The stab_sys function is a Python implemention of the
    Helmhert 7-parameter transformation, used to correct for common
    mode error. This builds on Prof Herring's stab_sys function in his
    tscon Fortran code. It uses a SVD approach to estimating the
    rotation matrix gathered from 'Computing Helmert Transformations'
    by G.A. Watson as well as its references. Note that units should
    be in meters, that is in the format from the level 2 processed
    UNAVCO pos files

    @param data_iterator: Expects an iterator that returns label, pandas dataframe
    @param metadata: Metadata that contains 'refXYZ' and 'refNEU'
    @param stab_min_NE: Optional minimum horizontal covariance parameter
    @param stab_min_U: Optional minimum vertical covariance parameter
    @param sigsc: Optional scaling factor for determining cutoff bounds for non stable sites
    @param errProp: Propagate errors through the transformation
    
    @return smSet, a reduced size dictionary of the data (in mm) for the sites in the specified geographic region,
            smHdr, a reduced size dictionary of the headers for the sites in the region
     '''
    
    # grabs all of the relevant data into labeled matrices
    smTestFlag = 0; numSites = 0; smSet = []; smHdr = [];
    smNEUcov = [];
    
    #grab specified sites from the given list of data, or defaults to using all of the sites

    for ii, pddata in data_iterator:
        # requires the minimum amount of data to be present
        # resamples these stations to daily

        if smTestFlag == 0:
            # grabbing position changes and the NEU change uncertainty
            # instead of positions ([2,3,4] and [11,12,13])
            #  --> had to put the factor of 1000 back in from raw stab processing
            smXYZ = pddata.loc[:,['X','Y','Z']] - metadata[ii]['refXYZ']
            smNEU = pddata.loc[:,['dN','dE','dU']]
            smNEcov = np.sqrt(pddata.loc[:,'Sn']**2 + pddata.loc[:,'Se']**2)
            smUcov = pddata.loc[:,'Su']**2
            smTestFlag = 1
            
        else:
            smXYZ = np.concatenate((smXYZ.T,(pddata.loc[:,['X','Y','Z']] - metadata[ii]['refXYZ']).T)).T
            smNEU = np.concatenate((smNEU.T,pddata.loc[:,['dN','dE','dU']].T)).T
            smNEcov = np.vstack((smNEcov,np.sqrt(pddata.loc[:,'Sn']**2 + pddata.loc[:,'Se']**2)))
            smUcov = np.vstack((smUcov,pddata.loc[:,'Su']**2))
        if errProp==1:
            smNEUcov.append(np.array(pddata.loc[:,['Sn','Se','Su','Rne','Rnu','Reu']]))
            
        # also keep the headers
        numSites += 1
        smSet.append(pddata)
        smHdr.append(metadata[ii])
        
    # grab the datelen from the last data chunk
    datelen = len(pddata)
            
    if numSites <= 1:
        # no or only 1 stations
        return dict(), dict()
    else:
        # do stabilization
        smNEcov = smNEcov.T
        smUcov = smUcov.T
        smNEUcov = np.array(smNEUcov)
        
        # minimum tolerances, number of sigma cutoff defined in input
        sNEtol = np.nanmax(np.vstack(((np.nanmedian(smNEcov,axis=1)-np.nanmin(smNEcov,axis=1)).T,np.ones((datelen,))*stab_min_NE)),axis=0)
        sUtol = np.nanmax(np.vstack(((np.nanmedian(smUcov,axis=1)-np.nanmin(smUcov,axis=1)).T,np.ones((datelen,))*stab_min_U)),axis=0)
        stable_site_idx = (np.nan_to_num(smNEcov-np.tile(np.nanmin(smNEcov,axis=1),(numSites,1)).T)<(sigsc*np.tile(sNEtol,(numSites,1)).T))
        stable_site_idx *= (np.nan_to_num(smUcov-np.tile(np.nanmin(smUcov,axis=1),(numSites,1)).T)<(sigsc*np.tile(sUtol,(numSites,1)).T))                                       
        if np.min(np.sum(stable_site_idx,axis=1)<3):
            warnings.warn('Fewer than 3 stabilization sites in part of this interval')                
        # compute the parameters for each time step
        stable_site_idx = np.repeat(stable_site_idx,3,axis=1)
        stable_site_idx[pd.isnull(smXYZ)] = False
        for ii in range(datelen):
            # cut out the nans for stable sites
            xyz = smXYZ[ii,stable_site_idx[ii,:]]
            xyz = np.reshape(xyz,[int(len(xyz)/3),3])
            neu = smNEU[ii,stable_site_idx[ii,:]]
            neu = np.reshape(neu,[int(len(neu)/3),3])
            # find mean and also remove it from the data
            xyzm = np.mean(xyz,axis=0)
            xyz = xyz - xyzm
            neum = np.mean(neu,axis=0)
            neu = neu - neum
            # using an SVD method instead
            U,s,V = np.linalg.linalg.svd(np.dot(xyz.T,neu))
            R=np.dot(U,V)
            sc = (np.sum(np.diag(np.dot(neu,np.dot(R.T,xyz.T)))))/(np.sum(np.diag(np.dot(xyz,xyz.T))))
            t = neum - sc*np.dot(xyzm,R)
            # looping over all sites to apply stabilization, including "stable" sites
            # no need to remove nans as transformed nans still nan
            xyz = smXYZ[ii,pd.isnull(smXYZ[ii,:])==False]
            xyz = np.reshape(xyz,[int(len(xyz)/3),3])
            smNEU[ii,pd.isnull(smXYZ[ii,:])==False] = np.reshape(np.dot(xyz,R)*sc + t,[len(xyz)*3,])
            
            # do error propagation
            if errProp==1:
                propagateErrors(R,sc,smNEUcov[:,ii,:])
            
            
        # fit back into the panda format overall data set, replaces original NEU, changes to mm units
        for jj in range(len(smSet)):
            smSet[jj].loc[:,['dN','dE','dU']] = smNEU[:,jj*3:(jj+1)*3]*1000
            # the "covariances" put back in also now in mm units
            if errProp==1:
                smSet[jj].loc[:,['Sn','Se','Su','Rne','Rnu','Reu']] = smNEUcov[jj,:,:]
        
        # returns the corrected data and the relevant headers as dictionaries, and the transformation's 7-parameters
        smSet_dict = dict(); smHdr_dict = dict()
        for ii in range(len(smHdr)):
            smSet_dict[smHdr[ii]['4ID']] = smSet[ii]
            smHdr_dict[smHdr[ii]['4ID']] = smHdr[ii]
        return smSet_dict, smHdr_dict



def propagateErrors(R,sc,stationCovs):
    '''
    Propagate GPS errors

    By writing out the R*E*R.T equations... to calculate the new covariance matrix
    without needing to form the matrix first as an intermediate step. Modifies
    covariance matrix in place

    @param R: Rotation matrix
    @param sc: Scaling value
    @param stationCovs: Station Covariances
    '''

    oldCs = stationCovs.copy()
    # need to make a copy to get the std & correlations to covariances
    oldCs[:,3] *= oldCs[:,0]*oldCs[:,1]
    oldCs[:,4] *= oldCs[:,0]*oldCs[:,2]
    oldCs[:,5] *= oldCs[:,1]*oldCs[:,2]
    oldCs[:,0] = oldCs[:,0]**2
    oldCs[:,1] = oldCs[:,1]**2
    oldCs[:,2] = oldCs[:,2]**2
    
    # calculate the modified covariances and reformat back to std and correlations
    stationCovs[:,0] = np.sqrt((sc**2)*np.dot(oldCs,[R[0,0]**2,R[0,1]**2,R[0,2]**2,
                               2*R[0,0]*R[0,1],2*R[0,0]*R[0,2],2*R[0,1]*R[0,2]]))
    stationCovs[:,1] = np.sqrt((sc**2)*np.dot(oldCs,[R[0,1]**2,R[1,1]**2,R[1,2]**2,
                               2*R[0,1]*R[1,1],2*R[0,1]*R[1,2],2*R[1,1]*R[1,2]]))
    stationCovs[:,2] = np.sqrt((sc**2)*np.dot(oldCs,[R[0,2]**2,R[1,2]**2,R[2,2]**2,
                               2*R[0,2]*R[1,2],2*R[0,2]*R[2,2],2*R[1,2]*R[2,2]]))
    stationCovs[:,3] = (sc**2)*np.dot(oldCs,[R[0,0]*R[0,1],R[0,1]*R[1,1],R[0,2]*R[1,2],
                R[0,1]**2+R[0,0]*R[1,1],R[0,1]*R[0,2]+R[0,0]*R[1,2],
                R[0,2]*R[1,1]+R[0,1]*R[1,2]])/(stationCovs[:,0]*stationCovs[:,1])
    stationCovs[:,4] = (sc**2)*np.dot(oldCs,[R[0,0]*R[0,2],R[0,1]*R[1,2],R[0,2]*R[2,2],
                R[0,0]*R[1,2]+R[0,1]*R[0,2],R[0,0]*R[2,2]+R[0,2]**2,
                R[0,1]*R[2,2]+R[0,2]*R[1,2]])/(stationCovs[:,0]*stationCovs[:,2])
    stationCovs[:,5] = (sc**2)*np.dot(oldCs,[R[0,2]*R[0,1],R[1,2]*R[1,1],R[1,2]*R[2,2],
                R[0,1]*R[1,2]+R[0,2]*R[1,1],R[0,1]*R[2,2]+R[0,2]*R[1,2],
                R[2,2]*R[1,1]+R[1,2]**2])/(stationCovs[:,1]*stationCovs[:,2])

    oldCs[:,0:3] *= 1000


def nostab_sys(allH,allD,timerng,indx=1,mdyratio=.7, use_progress_bar = True, index_date_only=False):
    '''
    Do not apply stabilization and simply returns stations after checking for sufficient amount of data

    @param allH: a dictionary of all of the headers of all sites loaded from the data directory
    @param allD: a dictionary of all of the panda format data of all of the corresponding sites
    @param timerng: an array with two string elements, describing the starting and ending dates
    @param indx: a list of site 4ID's indicating stations in the relevant geographic location, or 1 for all sites
    @param mdyratio: optional parameter for the minimum required ratio of data to determine if a sitef is kept for further analysis
    @param use_progress_bar: Display a progress bar
    @param index_date_only: When creating an index for the data, use date (not the time) only
 
    @return smSet, a reduced size dictionary of the data (in meters) for the sites in the specified geographic region and
            smHdr, a reduced size dictionary of the headers for the sites in the region
    '''
    
    # grabs all of the relevant data into labeled matrices
    numSites = 0; smSet = []; smHdr = [];
    datelen = pd.date_range(start=timerng[0],end=timerng[1],freq='D').shape[0]
    # needs the specified ratio of data to be present for further use. or number of days
    if mdyratio > 1:
        mindays = mdyratio
    else:
        mindays = ((pd.to_datetime(timerng[1]) - pd.to_datetime(timerng[0]))/pd.to_timedelta(1,'D'))*mdyratio
    
    #grab specified sites from the given list of data, or defaults to using all of the sites
    if indx == 1:
        indx = list(allH.keys())
    for ii in progress_bar(indx,enabled = use_progress_bar):

        if index_date_only:
            pddata = allD['data_' + ii][timerng[0]:timerng[1]]

        else:
            pddata = allD['data_' + ii]
            jd_conversion = 2400000.5
            pddata[pddata.index.name] = pddata.index
            pddata = pddata[[pddata.index.name] + pddata.columns.tolist()[:-1]]
            pddata.index = pd.to_datetime(pddata['JJJJJ.JJJJ'] + jd_conversion, unit='D', origin='julian')
            pddata.index.name = 'Date'
            pddata = pddata[timerng[0]:timerng[1]]


        dCheck = pddata[timerng[0]:timerng[1]].shape[0]

        if dCheck>mindays:
            # requires the minimum amount of data to be present
            # resamples these stations to daily
            if pddata.shape[0] < datelen:
                pddata = pddata.reindex(pd.date_range(start=timerng[0],end=timerng[1],freq='D'))
            else:
                pddata = pddata.reindex(pd.date_range(start=pddata.index[0],end=pddata.index[-1],freq='D'))
                
            # also keep the headers
            numSites += 1
            smSet.append(pddata)
            smHdr.append(allH[ii])
    
    # returns the data and the relevant headers as dictionaries, and the transformation's 7-parameters
    smSet_dict = dict(); smHdr_dict = dict()
    for ii in range(len(smHdr)):
        smSet_dict[smHdr[ii]['4ID']] = smSet[ii]
        smHdr_dict[smHdr[ii]['4ID']] = smHdr[ii]
    return smSet_dict, smHdr_dict


def removeAntennaOffset(antenna_offsets, data, window_start = pd.to_timedelta('4D'), window_end=pd.to_timedelta('4D'),min_diff=0.005, debug=False):
    '''
    Remove offsets caused by changes in antennas

    @param antenna_offsets: Pandas series of dates describing when the antenna changes were made
    @param data: Input GPS data
    @param window_start: Starting time before and after event to use for calculating offset
    @param window_end: Ending time before and after event to use before calculating offset
    @param min_diff: Minimum difference before and after offset to for applying correction
    @param debug: Enable debug output

    @return GPS data with the offsets removed
    '''
    if antenna_offsets is None:
        return data

    data_copy = data.copy()
    
    for full_offset in antenna_offsets:

        # truncate date
        offset = pd.to_datetime(pd.datetime(full_offset.year, full_offset.month, full_offset.day))

        if offset > (data.index[0] + window_end):
        
            before = data_copy.loc[(offset - window_end) - window_start : offset-window_start]
            after = data_copy.loc[offset + window_start : (offset + window_end) + window_start]

            if min(len(after.dropna()),len(before.dropna())) > 0:
                if np.abs(np.nanmedian(before) - np.nanmedian(after)) >= min_diff:                    
                    if debug == True:
                        print('fixing',offset, end=': ')
                        print(np.nanmedian(before)*1e3, np.nanmedian(after)*1e3)
                        
                    data_copy.loc[offset:] = data_copy.loc[offset:] + (np.nanmedian(before) - np.nanmedian(after))
                    if not pd.isnull(data_copy.loc[offset]):
                        data_copy.loc[offset] = np.nanmedian(pd.concat([before,
                                                                        data_copy.loc[offset + window_start : (offset + window_end) + window_start]]))
                    


    return data_copy
