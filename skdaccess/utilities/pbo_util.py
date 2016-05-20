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

"""@package pbo_util
Tools for working with PBO GPS data, including reference frame stabilization code
"""

from . import map_util as mo

import numpy as np
import pandas as pd
import warnings
from datetime import datetime
import tqdm


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

    @return array containg two tuples, lat_range and lon_range
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

def mogi(xdata, lat, lon, source_depth, amplitude):
    source_coords = (lat, lon)

    results = []

    for data in xdata:

        dim = data[0]
        station_coords = (float(data[1]),float(data[2]))
        # print(station_coords)

        y_distance = mo.wgs84_distance( source_coords, (station_coords[0], source_coords[1]) )
        x_distance = mo.wgs84_distance( source_coords, (source_coords[0], station_coords[1]) )

        x_distance = x_distance * np.sign(station_coords[1] - source_coords[1])
        y_distance = y_distance * np.sign(station_coords[0] - source_coords[0])


        R3 = (x_distance**2 + y_distance**2 + source_depth**2)**(3/2)

        result = None

        if dim == 'x':
            result = amplitude * x_distance / R3
        elif dim == 'y':
            result = amplitude * y_distance / R3
        elif dim == 'z':
            result = amplitude * source_depth / R3
        else:
            print("Did not understand dimension")

        results.append(result)
    return results

    
def finite_sphere(xdata, lat, lon, source_depth, amplitude, alpha_rad):
    '''
    Volcano Deformation, Dzurisin 2006, pg 290
    http://link.springer.com/book/10.1007/978-3-540-49302-0
    '''
    nu_v = .25
    C1 = (1+nu_v)/(2*(-7+5*nu_v))
    C2 = 15*(-2+nu_v)/(4*(-7+5*nu_v))
    source_coords = (lat, lon)

    results = []

    for data in xdata:

        dim = data[0]
        station_coords = (float(data[1]),float(data[2]))
        # print(station_coords)

        y_distance = mo.wgs84_distance( source_coords, (station_coords[0], source_coords[1]) )
        x_distance = mo.wgs84_distance( source_coords, (source_coords[0], station_coords[1]) )
        x_distance = x_distance * np.sign(station_coords[1] - source_coords[1])
        y_distance = y_distance * np.sign(station_coords[0] - source_coords[0])

        R3 = (x_distance**2 + y_distance**2 + source_depth**2)**(3/2)
        result = None
        if dim == 'x':
            result = amplitude *alpha_rad**3*(1+(alpha_rad/source_depth)**3*(C1+C2*source_depth**2/R3**(2/3))) * x_distance / R3
        elif dim == 'y':
            result = amplitude *alpha_rad**3*(1+(alpha_rad/source_depth)**3*(C1+C2*source_depth**2/R3**(2/3))) * y_distance / R3
        elif dim == 'z':
            result = amplitude *alpha_rad**3*(1+(alpha_rad/source_depth)**3*(C1+C2*source_depth**2/R3**(2/3))) * source_depth / R3
        else:
            print("Did not understand dimension")

        results.append(result)
    return results
    

def closed_pipe(xdata, lat, lon, source_depth, amplitude, pipe_delta):
    '''
    Volcano Deformation, Dzurisin 2006, pg 292
    http://link.springer.com/book/10.1007/978-3-540-49302-0
    '''
    nu_v = .25
    source_coords = (lat, lon)

    results = []

    for data in xdata:

        dim = data[0]
        station_coords = (float(data[1]),float(data[2]))
        # print(station_coords)

        y_distance = mo.wgs84_distance( source_coords, (station_coords[0], source_coords[1]) )
        x_distance = mo.wgs84_distance( source_coords, (source_coords[0], station_coords[1]) )
        x_distance = x_distance * np.sign(station_coords[1] - source_coords[1])
        y_distance = y_distance * np.sign(station_coords[0] - source_coords[0])

        result = None
        c1 = source_depth + pipe_delta
        c2 = source_depth - pipe_delta
        R_1 = (x_distance**2 + y_distance**2 + c1**2)**(1/2)
        R_2 = (x_distance**2 + y_distance**2 + c2**2)**(1/2)
        r2  = (x_distance**2 + y_distance**2)
        if dim == 'x':
            result = amplitude *((c1/R_1)**3+2*c1*(-3+5*nu_v)/R_1+(5*c2**3*(1-2*nu_v)-2*c2*r2*(-3+5*nu_v))/R_2**3) * x_distance / r2
        elif dim == 'y':
            result = amplitude *((c1/R_1)**3+2*c1*(-3+5*nu_v)/R_1+(5*c2**3*(1-2*nu_v)-2*c2*r2*(-3+5*nu_v))/R_2**3) * y_distance / r2
        elif dim == 'z':
            result = - amplitude *(c1**2/R_1**3+2*(-2+5*nu_v)/R_1+(c2**2*(3-10*nu_v)-2*r2*(-2+5*nu_v))/R_2**3)
        else:
            print("Did not understand dimension")

        results.append(result)
    return results
    
    
def constant_open_pipe(xdata, lat, lon, source_depth, amplitude, pipe_delta):
    '''
    Volcano Deformation, Dzurisin 2006, pg 295
    http://link.springer.com/book/10.1007/978-3-540-49302-0
    '''
    nu_v = .25
    source_coords = (lat, lon)

    results = []

    for data in xdata:

        dim = data[0]
        station_coords = (float(data[1]),float(data[2]))
        # print(station_coords)

        y_distance = mo.wgs84_distance( source_coords, (station_coords[0], source_coords[1]) )
        x_distance = mo.wgs84_distance( source_coords, (source_coords[0], station_coords[1]) )
        x_distance = x_distance * np.sign(station_coords[1] - source_coords[1])
        y_distance = y_distance * np.sign(station_coords[0] - source_coords[0])

        result = None
        c1 = source_depth + pipe_delta
        c2 = source_depth - pipe_delta
        R_1 = (x_distance**2 + y_distance**2 + c1**2)**(1/2)
        R_2 = (x_distance**2 + y_distance**2 + c2**2)**(1/2)
        r2  = (x_distance**2 + y_distance**2)
        if dim == 'x':
            result = amplitude *((c1/R_1)**3-2*c1*(1+nu_v)/R_1+(c2**3*(1+2*nu_v)+2*c2*r2*(1+nu_v))/R_2**3)* x_distance / r2
        elif dim == 'y':
            result = amplitude *((c1/R_1)**3-2*c1*(1+nu_v)/R_1+(c2**3*(1+2*nu_v)+2*c2*r2*(1+nu_v))/R_2**3)* y_distance / r2
        elif dim == 'z':
            result = - amplitude *(c1**2/R_1**3-2*nu_v/R_1+(-c2**2+2*R_2**2*nu_v)/R_2**3)
        else:
            print("Did not understand dimension")

        results.append(result)
    return results
    
       
def rising_open_pipe(xdata, lat, lon, source_depth, amplitude, pipe_delta,open_pipe_top):
    '''
    Volcano Deformation, Dzurisin 2006, pg 295
    http://link.springer.com/book/10.1007/978-3-540-49302-0
    '''
    nu_v = .25
    source_coords = (lat, lon)

    results = []

    for data in xdata:

        dim = data[0]
        station_coords = (float(data[1]),float(data[2]))
        # print(station_coords)

        y_distance = mo.wgs84_distance( source_coords, (station_coords[0], source_coords[1]) )
        x_distance = mo.wgs84_distance( source_coords, (source_coords[0], station_coords[1]) )
        x_distance = x_distance * np.sign(station_coords[1] - source_coords[1])
        y_distance = y_distance * np.sign(station_coords[0] - source_coords[0])

        result = None
        c0 = open_pipe_top
        c1 = source_depth + pipe_delta
        R_0 = (x_distance**2 + y_distance**2 + c0**2)**(1/2)
        R_1 = (x_distance**2 + y_distance**2 + c1**2)**(1/2)
        r2  = (x_distance**2 + y_distance**2)
        if dim == 'x':
            result = amplitude *(-(c0**2/R_0**3)+2*nu_v/R_0+(c1**2-2*(c1**2+r2)*nu_v)/R_1**3)* x_distance / c1
        elif dim == 'y':
            result = amplitude *(-(c0**2/R_0**3)+2*nu_v/R_0+(c1**2-2*(c1**2+r2)*nu_v)/R_1**3)* y_distance / c1
        elif dim == 'z':
            result = -amplitude *((c0**3/R_0**3)-c1**3/R_1**3+c1*(-1+2*nu_v)/R_1+c0*(1-2*nu_v)/R_0+(-1+2*nu_v)*np.log(c0+R_0)-(-1+2*nu_v)*np.log(c1+R_1))/ c1
        else:
            print("Did not understand dimension")

        results.append(result)
    return results
    
    
def sill(xdata, lat, lon, source_depth, amplitude):
    '''
    Volcano Deformation, Dzurisin 2006, pg 297
    http://link.springer.com/book/10.1007/978-3-540-49302-0
    '''
    source_coords = (lat, lon)
    results = []

    for data in xdata:

        dim = data[0]
        station_coords = (float(data[1]),float(data[2]))
        # print(station_coords)

        y_distance = mo.wgs84_distance( source_coords, (station_coords[0], source_coords[1]) )
        x_distance = mo.wgs84_distance( source_coords, (source_coords[0], station_coords[1]) )
        x_distance = x_distance * np.sign(station_coords[1] - source_coords[1])
        y_distance = y_distance * np.sign(station_coords[0] - source_coords[0])

        R5 = (x_distance**2 + y_distance**2 + source_depth**2)**(5/2)
        result = None
        if dim == 'x':
            result = amplitude * x_distance * source_depth**2 / R5
        elif dim == 'y':
            result = amplitude * y_distance * source_depth**2 / R5
        elif dim == 'z':
            result = amplitude * source_depth**3 / R5
        else:
            print("Did not understand dimension")

        results.append(result)
    return results
    
    
def getEigenvectors(pcaRes, geo_point, stationList, info_dict):
        '''
        returns the eigenvectors, all pointing "outward" for plotting
        '''
        n_stations = len(stationList)
        f_pca = pcaRes['CA']
        component = 1
        
        eigen_vectors = []
        for i in range(n_stations):
            eigen_vectors.append((f_pca.components_[component-1][i*2+1], f_pca.components_[component-1][i*2]))

        dd = 0.01 #fixed distance for evaluating new coordinate
        in_cnt = 0; out_cnt = 0; null_cnt = 0
        poi_coord = np.array(geo_point)*np.pi/180
        for jj in range(0,len(stationList)):
            # check overall horizontal movement as in or out configuration
            ii = stationList[jj]
            coord = (info_dict[ii]['refNEU'][0]*np.pi/180,(info_dict[ii]['refNEU'][1]-360)*np.pi/180)
            dist = 6371*2*np.arcsin(np.sqrt(np.sin((poi_coord[0]-coord[0])/2)**2
                                    +np.cos(poi_coord[0])*np.cos(coord[0])*(np.sin((poi_coord[1]-coord[1])/2))**2))
            eig_ang = np.arctan2(eigen_vectors[jj][1],eigen_vectors[jj][0])
            ncoord = (coord[0]+dd*np.sin(eig_ang)*np.pi/180,coord[1]+dd*np.cos(eig_ang)*np.pi/180)                
            ndist = 6371*2*np.arcsin(np.sqrt(np.sin((poi_coord[0]-ncoord[0])/2)**2
                                    +np.cos(poi_coord[0])*np.cos(ncoord[0])*(np.sin((poi_coord[1]-ncoord[1])/2))**2))
            if ndist>dist:
                out_cnt += 1
            elif ndist<dist:
                in_cnt += 1
            else:
                null_cnt += 1
        # flip eigenvectors and projection
        if in_cnt>(out_cnt+null_cnt):
            eigen_vectors = (np.array(eigen_vectors)*-1).tolist()
            pcaRes['Projection'] *= -1

        return eigen_vectors

        
        
## The stab_sys function is a Python implemention of the Helmhert 7-parameter
#  transformation, used to correct for common mode error. This builds on
#  Prof Herring's stab_sys function in his tscon Fortran code. It uses a SVD
#  approach to estimating the rotation matrix gathered from 'Computing Helmert
#  Transformations' by G.A. Watson as well as its references. Note that units
#  should be in meters, that is in the format from the level 2 processed
#  UNAVCO pos files
#  Input:
#   - allH, a dictionary of all of the headers of all sites loaded from the data directory
#   - allD, a dictionary of all of the panda format data of all of the corresponding sites
#   - timerng, an array with two string elements, describing the starting and ending dates
#   - indx, a list of site 4ID's indicating stations in the relevant geographic location
#   - stab_min_NE, optional minimum horizontal covariance parameter
#   - stab_min_U, optional minimum vertical covariance parameter
#   - sigsc, optional scaling factor for determining cutoff bounds for non-stable sites
#   - mdyratio, optional parameter for the minimum required ratio of data to determine if a site is kept for further analysis
#
#  Output:
#   - smSet, a reduced size dictionary of the data for the sites in the specified geographic region
#   - smHdr, a reduced size dictionary of the headers for the sites in the region
#   - R, the calculated 3x3 rotation matrix
#   - sc, the scaling parameter
#   - t, the translation 3x1 vector
def stab_sys(allH,allD,timerng,indx=1,stab_min_NE=.0005,stab_min_U=.005,sigsc=2,mdyratio=.7,errProp=0):
    # grabs all of the relevant data into labeled matrices
    smTestFlag = 0; numSites = 0; smSet = []; smHdr = [];
    datelen = pd.date_range(start=timerng[0],end=timerng[1],freq='D').shape[0]
    smNEUcov = []
    # needs the specified ratio of data to be present for further use. or at least 2 years
    if mdyratio == 0:
        mindays = 731
    else:
        mindays = ((datetime.strptime(timerng[1],"%Y-%m-%d")-datetime.strptime(timerng[0],"%Y-%m-%d")).days)*mdyratio   
    
    #grab specified sites from the given list of data, or defaults to using all of the sites
    if indx == 1:
        indx = allH.keys()
    if 'Snow' in allD['data_' + indx[0]].keys():
        snowDat = 1
    else:
        snowDat = 0
    for ii in tqdm.tqdm(indx):
        if snowDat == 0:
            dCheck = allD['data_' + ii][timerng[0]:timerng[1]].shape[0]
        elif snowDat == 1:
            dCheck = sum(np.isfinite(allD['data_' + ii][timerng[0]:timerng[1]]['dN']))
        if dCheck>mindays:
            # requires the minimum amount of data to be present
            # resamples these stations to daily
            pddata = allD['data_' + ii][timerng[0]:timerng[1]]
            if pddata.shape[0] < datelen:
                pddata = pddata.reindex(pd.date_range(start=timerng[0],end=timerng[1],freq='D'))
            else:
                pddata = pddata.reindex(pd.date_range(start=pddata.index[0],end=pddata.index[-1],freq='D'))
            if smTestFlag == 0:
                # grabbing position changes and the NEU change uncertainty
                # instead of positions ([2,3,4] and [11,12,13])
                smXYZ = pddata.ix[:,[2,3,4]] - allH[ii]['refXYZ']
                smNEU = pddata.ix[:,[14,15,16]]
                smNEcov = np.sqrt(pddata.ix[:,17]**2 + pddata.ix[:,18]**2)
                smUcov = pddata.ix[:,19]**2
                smTestFlag = 1
                
            else:
                smXYZ = np.concatenate((smXYZ.T,(pddata.ix[:,[2,3,4]] - allH[ii]['refXYZ']).T)).T
                smNEU = np.concatenate((smNEU.T,pddata.ix[:,[14,15,16]].T)).T
                smNEcov = np.vstack((smNEcov,np.sqrt(pddata.ix[:,17]**2 + pddata.ix[:,18]**2)))
                smUcov = np.vstack((smUcov,(pddata.ix[:,19]**2)))
            if errProp==1:
                smNEUcov.append(np.array(pddata.ix[:,17:23]))
                
            # also keep the headers
            numSites += 1
            smSet.append(pddata)
            smHdr.append(allH[ii])
            
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
        xyz = np.reshape(xyz,[len(xyz)/3,3])
        neu = smNEU[ii,stable_site_idx[ii,:]]
        neu = np.reshape(neu,[len(neu)/3,3])
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
        xyz = np.reshape(xyz,[len(xyz)/3,3])
        smNEU[ii,pd.isnull(smXYZ[ii,:])==False] = np.reshape(np.dot(xyz,R)*sc + t,[len(xyz)*3,])
        
        # do error propagation
        if errProp==1:
            propagateErrors(R,sc,smNEUcov[:,ii,:])
        
        
    # fit back into the panda format overall data set, replaces original NEU, changes to mm units
    for jj in range(len(smSet)):
        smSet[jj].ix[:,14:17] = smNEU[:,jj*3:(jj+1)*3]*1000
        # the "covariances" put back in also now in mm units
        if errProp==1:
            smSet[jj].ix[:,17:23] = smNEUcov[jj,:,:]
    
    # returns the corrected data and the relevant headers as dictionaries, and the transformation's 7-parameters
    smSet_dict = dict(); smHdr_dict = dict()
    for ii in range(len(smHdr)):
        smSet_dict[smHdr[ii]['4ID']] = smSet[ii]
        smHdr_dict[smHdr[ii]['4ID']] = smHdr[ii]
    return smSet_dict, smHdr_dict



def propagateErrors(R,sc,stationCovs):
    # by writing out the R*E*R.T equations... to calculate the new covariance matrix
    # without needing to form the matrix first as an intermediate step

    oldCs = stationCovs.copy()
    # need to make a copy to get the std & correlations to covariances
    oldCs[:,0:3] *= 1e3
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



## The nostab_sys function does not apply stabilization and simply returns 
#  stations after checking for sufficient amount of data
#  Input:
#   - allH, a dictionary of all of the headers of all sites loaded from the data directory
#   - allD, a dictionary of all of the panda format data of all of the corresponding sites
#   - timerng, an array with two string elements, describing the starting and ending dates
#   - indx, a list of site 4ID's indicating stations in the relevant geographic location
#   - mdyratio, optional parameter for the minimum required ratio of data to determine if a site is kept for further analysis
#
#  Output:
#   - smSet, a reduced size dictionary of the data for the sites in the specified geographic region
#   - smHdr, a reduced size dictionary of the headers for the sites in the region
def nostab_sys(allH,allD,timerng,indx=1,mdyratio=.7):
    # grabs all of the relevant data into labeled matrices
    numSites = 0; smSet = []; smHdr = [];
    datelen = pd.date_range(start=timerng[0],end=timerng[1],freq='D').shape[0]
    # needs the specified ratio of data to be present for further use. or at least 2 years
    if mdyratio == 0:
        mindays = 731
    else:
        mindays = ((datetime.strptime(timerng[1],"%Y-%m-%d")-datetime.strptime(timerng[0],"%Y-%m-%d")).days)*mdyratio   
    
    #grab specified sites from the given list of data, or defaults to using all of the sites
    if indx == 1:
        indx = allH.keys()
    if 'Snow' in allD['data_' + indx[0]].keys():
        snowDat = 1
    else:
        snowDat = 0
    for ii in tqdm.tqdm(indx):
        if snowDat == 0:
            dCheck = allD['data_' + ii][timerng[0]:timerng[1]].shape[0]
        elif snowDat == 1:
            dCheck = sum(np.isfinite(allD['data_' + ii][timerng[0]:timerng[1]]['dN']))
        if dCheck>mindays:
            # requires the minimum amount of data to be present
            # resamples these stations to daily
            pddata = allD['data_' + ii][timerng[0]:timerng[1]]
            if pddata.shape[0] < datelen:
                pddata = pddata.reindex(pd.date_range(start=timerng[0],end=timerng[1],freq='D'))
            else:
                pddata = pddata.reindex(pd.date_range(start=pddata.index[0],end=pddata.index[-1],freq='D'))
                
            # also keep the headers
            numSites += 1
            smSet.append(pddata)
            smHdr.append(allH[ii])
    
    # returns the corrected data and the relevant headers as dictionaries, and the transformation's 7-parameters
    smSet_dict = dict(); smHdr_dict = dict()
    for ii in range(len(smHdr)):
        smSet_dict[smHdr[ii]['4ID']] = smSet[ii]
        smHdr_dict[smHdr[ii]['4ID']] = smHdr[ii]
    return smSet_dict, smHdr_dict

