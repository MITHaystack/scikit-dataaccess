# The MIT License (MIT)
# Copyright (c) 2016 Massachusetts Institute of Technology
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
# THE SOFTWARE

"""@package data_util
Provides utilities for handling data.
"""
import gzip
import tarfile
import glob
import re
from urllib.request import urlopen
from shutil import copyfileobj
import pandas as pd
import numpy as np
import io
import tqdm
import warnings
import tables
import pickle
from ftplib import FTP
from collections import defaultdict
from collections import OrderedDict
from astropy.io import fits
from astropy.table import Table
from tarfile import TarFile
from io import BytesIO

import configparser
import os

def getConfig():
    '''
    Retrieve skdaccess configuration

    @return configParser.ConfigParser object of configuration
    '''
    config_location = os.path.expanduser('~') + '/.skdaccess.conf'

    conf = configparser.ConfigParser()
    conf.read(config_location)

    return conf

def writeConfig(conf):
    '''
    Write config to disk

    @param configparser.ConfigParser object
    '''
    config_location = os.path.expanduser('~') + '/.skdaccess.conf'
    config_handle = open(config_location, "w")
    conf.write(config_handle)
    config_handle.close()


def getDataLocation(data_name):
    ''' 
    Get the location of data set

    @param data_name: Name of data set
    
    @return string of data location, None if not found
    '''
    data_name = str.lower(data_name)

    conf = getConfig()
    return conf.get(data_name, 'data_location', fallback=None)

def setDataLocation(data_name, location):
    '''
    Set the location of a data set

    @param data_name: Name of data set
    @param location: Location of data set
    '''
    
    conf = getConfig()

    if not conf.has_section(data_name):
        conf.add_section(data_name)

    conf.set(data_name, 'data_location', location)
    writeConfig(conf)



def downloadPBO(out_file = 'pbo_data.h5', use_file=None):
    '''
    Download and parse data from the Plate Boundary Observatory

    @param out_file: Output filename for parsed data
    @param use_file: Use already downloaded data. If None, data will be downloaded.

    @return Absolute path of parsed data
    '''

    def convert_timedelta(in_number):
        time_string = str(in_number)
        time_string = time_string[0:2] + ':'  + time_string[2:4] + ':' + time_string[4:]
        return pd.to_timedelta(time_string)


    if use_file is None:
        print("Downloading pbo data")
        
        filename = 'pbo.nam08.pos.tar.gz'
        ftp = FTP('data-out.unavco.org')
        ftp.login()
        ftp.cwd('/pub/products/position/')
        ftp.retrbinary('RETR ' + filename, open(filename, 'wb').write)
        ftp.quit()
        
        print("Download complete")
    else:
        filename = use_file


    tar = tarfile.open(filename)
    store = pd.HDFStore(out_file, complib='zlib', complevel=5)


    member_list = [member for member in tar.getmembers() if member.name[-3:] == 'pos']
    names = list()
    meta_data = defaultdict(list)

    for info in tqdm.tqdm(member_list):
        match = re.match('[A-Z0-9]{4}',info.name)
        name = match.group(0)    
        stringio = io.StringIO(tar.extractfile(info).read().decode('utf-8'))

        data = pd.read_fwf(stringio, skiprows=36,index_col=0,parse_dates=[0],
                           widths = [9,7,11, 15, 15, 15, 9, 9, 9, 7, 7, 7,
                                     19, 16, 11, 12, 10, 10, 11, 9, 9, 7, 7, 7, 6])

        store.put('data_' + name,data,format='table')

        stringio.seek(0)
        res = []
        for i in range(9):
            res.append(stringio.readline().strip())

        if res[2][-4:] != name:
            raise Exception("filename does not match header information!")

        names.append(name)

        refXYZ = [float(res[7].split()[ii]) for ii in [4,5,6]]
        refNEU = [float(res[8].split()[ii]) for ii in [4,5,6]]


        meta_data['station_name'].append(res[3][16:])
        meta_data['start_epoch'].append(res[4][16:].strip())
        meta_data['last_epoch'].append(res[5][16:].strip())


        meta_data['X_ref'].append(refXYZ[0])
        meta_data['Y_ref'].append(refXYZ[1])
        meta_data['Z_ref'].append(refXYZ[2])

        meta_data['N_ref'].append(refNEU[0])
        meta_data['E_ref'].append(refNEU[1])
        meta_data['U_ref'].append(refNEU[2])


        meta_data['XYZ_units'].append('meters') 
        meta_data['XYZ_ref_frame'].append( res[7].split(' ')[-1]) 
        meta_data['NEU_units'].append('degrees + meters'),
        meta_data['NEU_ref_frame'].append(res[8].split(' ')[-1])



    cols = ['station_name', 'start_epoch', 'last_epoch',
            'X_ref', 'Y_ref', 'Z_ref', 'N_ref','E_ref','U_ref',
            'XYZ_units','XYZ_ref_frame','NEU_units','NEU_ref_frame']
    store.put('meta_data', pd.DataFrame(meta_data,index=names)[cols], format='table')
    store.close()

    return os.path.abspath(out_file)

def downloadGRACE(out_file = 'grace.h5', local_data = None):
    '''
    Download and parse data from the Gravity Recovery and Climate Experiment.

    @param out_file: Output filename for parsed data
    @param local_data: Use already downloaded data. If None, data will be downloaded.

    @return Absolute path of parsed data
    '''
    # Get date of grace data from filename
    def getDate(filename):
        return pd.to_datetime(re.search('[0-9]{8}',filename).group())

    # Check if two dates are within 10 days of eachother
    def dateMismatch(date1,date2):
        if np.abs(date1 - date2) > pd.to_timedelta(10, 'D'):
            return True
        else:
            return False

    def roundDay(timestamp):
        start_date = pd.Timestamp(timestamp.date())
        time = timestamp - start_date
        if(time > pd.Timedelta(12,'h')):
            final_date = start_date + pd.Timedelta(1,'D')
        else:
            final_date = start_date

        return final_date
    
    if local_data is None:
        print("Downloading GRACE Land Mass Data")
        local_data = 'grace_files'
        ftp = FTP("podaac-ftp.jpl.nasa.gov")
        ftp.login()
        ftp.cwd('/allData/tellus/L3/land_mass/RL05/ascii')
        dir_list = list(ftp.nlst(''))
        file_list = [file for file in dir_list if re.search('.txt.gz$', file)]
        os.mkdir(local_data)
        for file in tqdm.tqdm(file_list):
            ftp.retrbinary('RETR ' + file, open('grace_files/'+file, 'wb').write)
        ftp.quit()


    scale_factors = pd.read_table(local_data + "/CLM4.SCALE_FACTOR.DS.G300KM.RL05.DSTvSCS1409.txt.gz", 
                         skiprows=14, header=None, engine='python', sep='\s+',
                         names=['Lon', 'Lat', 'LWET']).pivot(columns='Lon', index='Lat')['LWET']
    leakage_unc = pd.read_table(local_data + '/CLM4.LEAKAGE_ERROR.DS.G300KM.RL05.DSTvSCS1409.txt.gz', skiprows=14,
                                  header=None, engine='python', sep='\s+', 
                                  names=['Lon','Lat','Uncertainty']).pivot(columns='Lon', index='Lat')['Uncertainty']
    measurment_unc = pd.read_table(local_data + '/CLM4.MEASUREMENT_ERROR.DS.G300KM.RL05.DSTvSCS1409.txt.gz', skiprows=14,
                                  header=None, engine='python', sep='\s+', 
                                  names=['Lon','Lat','Uncertainty']).pivot(columns='Lon', index='Lat')['Uncertainty']

    total_unc = np.sqrt(leakage_unc**2 + measurment_unc**2)                


    jpl_files = glob.glob(local_data + '/GRCTellus.JPL.*')
    csr_files = glob.glob(local_data + '/GRCTellus.CSR.*')
    gfz_files = glob.glob(local_data + '/GRCTellus.GFZ.*')

    jpl_files.sort()
    csr_files.sort()
    gfz_files.sort()


    # Data is not released simultenously, so only take months present in all three data sets
    min_length = np.min((len(jpl_files), len(csr_files), len(gfz_files)))
    jpl_files = jpl_files[:min_length]
    csr_files = csr_files[:min_length]
    gfz_files = gfz_files[:min_length]


    data = {}
    u_dict = {}

    print('Parsing Grace data')
    for file_list in tqdm.tqdm(zip(jpl_files, csr_files, gfz_files), total=min_length):

        # Check for date mismatch
        jpl_date = getDate(file_list[0])
        csr_date = getDate(file_list[1])
        gfz_date = getDate(file_list[2])

        if dateMismatch(jpl_date, csr_date):
            print("JPL and CSR date Mismatch:", jpl_date, csr_date)

        if dateMismatch(jpl_date, gfz_date):
            print("JPL and GFZ date Mismatch:", jpl_date, gfz_date)

        if dateMismatch(csr_date, gfz_date):
            print("CSR and GFZ date Mismatch:", csr_date, gfz_date)


        # Create keylist
        key_list = [jpl_date, csr_date, gfz_date]

        scaled_list = []
        unscaled_list = []
        for file in file_list:

            grace_data = pd.read_table(file, skiprows=22, header=None, engine='python', sep='\s+',
                                   names=['Lon', 'Lat', 'LWET']).pivot(columns='Lon', index='Lat')
            unscaled = pd.read_table(file, skiprows=22, header=None, engine='python', sep='\s+',
                                 names=['Lon', 'Lat', 'LWET']).pivot(columns='Lon', index='Lat')

            grace_data *= scale_factors

            scaled_list.append(grace_data)
            unscaled_list.append(unscaled)

        # Since the three datasets are centered on different days,
        # use the average to center them.
        keys = pd.Series(key_list) 
        start = keys.min()
        newkey = (keys - start).mean() + start
        newkey = roundDay(newkey)
        key = newkey

        # Now store the results in a dictionary
        grace_data = pd.concat(scaled_list).groupby(level=0).mean()
        data[key] = (grace_data['LWET'])



    data = pd.Panel(data)
    store = pd.HDFStore(out_file,complib='zlib', complevel=5)
    store.put('grace', data, format='table')
    store.put('uncertainty', total_unc, format='table')
    store.close()

    return os.path.abspath(out_file)

def downloadGW(out_file = 'gw_data.h5', local_data = None):
    '''
    Download and parse California groundwater data provided by USGS

    @param out_file: Output filename for parsed data
    @param local_data: Use already downloaded data. If None, data will be downloaded.

    @return Absolute path of parsed data
    '''

    # If using local data metadata name is assumed
    metadata_filename = 'gw_metadata.rdb'

    if local_data is None:
        print("Downloading data from USGS")
        # Download data
        data_filename = 'gw_data.rdb'        

        data_file = open(data_filename, 'wb')
        copyfileobj(urlopen('http://waterservices.usgs.gov/nwis/dv/?format=rdb&stateCd=ca&startDT=1800-01-01&endDT=2020-12-31&statCd=00008&parameterCd=72019&siteType=GW'),
                    data_file)
        data_file.close()


        # Download meta data
        data_file = open(metadata_filename, 'wb')
        copyfileobj(urlopen('http://waterservices.usgs.gov/nwis/site/?format=rdb&stateCd=ca&startDT=1800-01-01&endDT=2020-12-31&parameterCd=72019&siteType=GW&hasDataTypeCd=dv'),
                    data_file)
        data_file.close()
        
        print("Download complete")
    else:
        data_filename = local_data

    
    full_data = open(data_filename).read()
    stations = re.findall('#    USGS ([0-9]*)', full_data, re.MULTILINE)
    store = pd.HDFStore(out_file, complevel=5, complib='blosc')

    # Parse data
    print('Parsing data')
    for station in tqdm.tqdm(stations):
        dates = []
        water_depth = []
        data_qual = []
        st_full_data = re.findall('^USGS\s+' + station + '.*', full_data, re.MULTILINE)
        for line in st_full_data:
            split_line = line.split('\t')
            try:
                depth = float(split_line[3]) * 0.3048
            except:
                depth = np.NaN
            water_depth.append(depth)
            dates.append(pd.to_datetime(split_line[2]))
            data_qual.append(split_line[4])


        water_depth = pd.Series(water_depth, index=dates,name="Water Depth")
        data_qual = pd.Series(data_qual, index=dates,name="Data Quality")
        full_results = pd.concat([water_depth, data_qual],axis=1)
        store.put('USGS' + station, full_results, format='table')


    #Read metadata
    meta_data = pd.read_table(metadata_filename, skiprows=31, names = ['Agency', 'Site Number', 'Site Name', 'Site Type', 
                                                                       'Lat', 'Lon', 'LatLon Accuracy', 'LatLon Datum',
                                                                       'Altitude', 'Altitude Accuracy', 'Altitude Datum',
                                                                       'Hydrologic Code'], index_col=1)

    meta_data['Altitude'] *= 0.3048
    meta_data['Altitude Accuracy'] *= 0.3048

    int_stations = [int(station) for station in stations]
    
    meta_data = meta_data.loc[int_stations]

    store.put('meta_data',meta_data,format='table')
    store.close()

    return os.path.abspath(out_file)

def downloadKeplerData(kid_list):
    '''
    Download and parse Kepler data for a list of kepler id's

    @param kid_list: List of Kepler ID's to download

    @return dictionary of kepler data
    '''

    return_data = dict()

    # connect to ftp server
    ftp = FTP('archive.stsci.edu')
    ftp.login()

    # For each kepler id, download the appropriate data
    for kid in kid_list:
        ftp.cwd('/pub/kepler/lightcurves/' + kid[0:4] + '/' + kid)
        file_list = ftp.nlst()
        filename = None
        for file in file_list:
            match = re.match('kplr' + kid + '_lc_.*',file)
            if match:
                filename = match.group(0)
                break

        bio = BytesIO()
        ftp.retrbinary('RETR ' + filename, bio.write)
        bio.seek(0)

        # Read tar file
        tfile = tfile = TarFile(fileobj=bio)
        member_list = [member for member in tfile.getmembers()]

        # Extract data from tar file
        data_list = []
        for member in member_list:
            file = tfile.extractfile(member)
            fits_data = fits.open(file)
            data = Table(fits_data[1].data).to_pandas()
            data.set_index('TIME',inplace=True)
            data.loc[:,'QUARTER'] = fits_data[0].header['QUARTER']
            data_list.append(data)
        full_data = pd.concat(data_list)
        return_data[kid] = full_data

    try:
        ftp.quit()
    except:
        ftp.close()

    return return_data
