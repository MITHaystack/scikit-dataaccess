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

# """@package PBO
# Provides classes for accessing PBO data.
# """

# mithagi required Base,Utils imports
from skdaccess.framework.data_class import DataFetcherStorage, TableWrapper
from skdaccess.utilities import pbo_util

# Standard library imports
from ftplib import FTP
import tarfile
from zipfile import ZipFile
import re
from collections import defaultdict
from six.moves.urllib.request import urlopen
from shutil import copyfileobj
import io
import os
from glob import glob



# 3rd party package imports
import pandas as pd
from tqdm import tqdm


class DataFetcher(DataFetcherStorage):
    ''' 
    Data fetcher for PBO GPS data
    '''
    
    def __init__(self, start_time, end_time, ap_paramList, mdyratio=.5,
                 default_columns = ['dN','dE','dU'],
                 default_error_columns = ['Sn', 'Se', 'Su'],
                 use_progress_bar = True, index_date_only=True):
        ''' 
        Initialize a DataFetcher

        @param start_time: String of starting date in the form of "2005-01-01"
        @param end_time: String of ending date in the form of "2014-12-31"
        @param ap_paramList[lat_range]: AutoList, Latitude range used to select stabilization sites
        @param ap_paramList[lon_range]: AutoList, Longitude range used to select stabilization sites
        @param mdyratio: Only keep stations that have mdyratio of data in the specified time range
        @param default_columns: Default columns to process
        @param default_error_columns: Default error columns to process
        @param use_progress_bar: Use a progress bar when loading data
        @param index_date_only: Create a index using date only (no hour information)
        '''
        
        self._start_time = start_time
        self._end_time = end_time
        self.station_list = None
        self._mdyratio = mdyratio
        self.default_columns = default_columns
        self.default_error_columns = default_error_columns
        self.use_progress_bar = use_progress_bar
        self.index_date_only = index_date_only

        self.antenna_info = DataFetcher.getAntennaLogs()
        
        self.meta_data = DataFetcher.getStationMetadata()

        super(DataFetcher,self).__init__(ap_paramList)
        

    def setStationList(self, station_list):
        '''
        Set the list of stations to use

        @param station_list: List of stations to fetch
        '''
        self.station_list = station_list

    

    def _rawData(self):
        ''' 
        Select data from sites within site radius to be returned without stabilization.
        ''' 
        storeName = self.meta_data
        keyList = self._validStations(storeName)
        if len(keyList) == 0:
            self._validInit = 0
        else:
            storeData_fn = DataFetcher.getDataLocation('pbo')
            if storeData_fn is None:
                print('Dataset not available')
                return None
    
            storeData = pd.HDFStore(storeData_fn, 'r')
            mdyratio = self._mdyratio
            
            smSet_all, smHdr_all = pbo_util.nostab_sys(storeName,storeData,[self._start_time,self._end_time],indx=keyList,mdyratio=mdyratio,
                                                       use_progress_bar = self.use_progress_bar, index_date_only=self.index_date_only)
    
            self._smSet_all = smSet_all
            self._smHdr_all = smHdr_all
            storeData.close()
            if len(self._smSet_all) == 0:
                self._validInit = 0
            else:
                self._validInit = 1
            
    def _validStations(self,storeName):
            
        # pulled this out from stab and raw functions
        geospace = [self.ap_paramList[0](), self.ap_paramList[1]()]
        
        keyList =[]
        for ii in storeName.keys():
            coord = storeName[ii]['refNEU']
            if coord[0]>=geospace[0][0] and coord[0]<geospace[0][1] and coord[1]>=geospace[1][0] and coord[1]<geospace[1][1]:
                keyList.append(storeName[ii]['4ID'])
            elif coord[0]>=geospace[0][0] and coord[0]<geospace[0][1] and coord[1]>=(360+geospace[1][0]) and coord[1]<(360+geospace[1][1]):
                keyList.append(storeName[ii]['4ID'])
        return keyList
        

    def getInfo(self):
        ''' 
        Get information about the stations and geo_point

        @return tuple containing station list and geo_point
        '''

        storeName = self.meta_data
                    
        if self.station_list == None:
            # if no station_list defined, use all stations in stab_region
            try:
                station_list = list(self._smHdr_all.keys())
            except:
                station_list = self._validStations(storeName)            
        else:
            # otherwise, use the defined station_list
            station_list = self.station_list

        return station_list
        

    def output(self):
        '''
        Generate PBO Data Wrapper

        @return PBO Data Wrapper
        '''

        self._rawData()
        
        if self._validInit==1:
    
            return(TableWrapper(self._smSet_all, meta_data=self._smHdr_all, default_columns=self.default_columns,
                                default_error_columns = self.default_error_columns))
    
        else:
            return TableWrapper(dict(), default_columns=self.default_columns,
                                default_error_columns = self.default_error_columns)


    def __str__(self):
        '''
        print the parameter values

        @return String representation of Data Fetcher
        '''
        return 'PBO Data Fetcher' + super(DataFetcher, self).__str__()


    def getStationMetadata(data_frame=False):
        '''
        Read in the metadata and convert to dictionary

        @return dictionary of PBO metadata
        '''

        storeData_fn = DataFetcher.getDataLocation('pbo')
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
            meta_data[site]['Lat'] = data['N_ref']
            meta_data[site]['Lon'] = data['E_ref'] - 360
            meta_data[site]['4ID'] = site

        store.close()

        if data_frame:
            metadata_frame = pd.DataFrame.from_dict(meta_data, orient='index')
            metadata_frame['X'] = [data[0] for data in metadata_frame['refXYZ']]
            metadata_frame['Y'] = [data[1] for data in metadata_frame['refXYZ']]
            metadata_frame['Z'] = [data[2] for data in metadata_frame['refXYZ']]
            metadata_frame['Height'] = [data[2] for data in metadata_frame['refNEU']]

            metadata_frame.drop(labels=['refNEU','refXYZ', '4ID'], inplace=True, axis=1)
            return metadata_frame

        else:
            return meta_data

    def getAntennaLogs():
        '''
        Get antenna logs.
        
        @return dictionary of data frames containing antenna logs
        '''

        meta_data = DataFetcher.getStationMetadata()
        
        storeData_fn = DataFetcher.getDataLocation('pbo')
        if storeData_fn is None:
            print('Dataset not available')
            return None

        store = pd.HDFStore(storeData_fn, 'r')
        logs = store['/antenna_logs']

        antenna_dict = dict()

        # for label in meta_data.keys():
        #     try:
        #         antenna_dict[label] = store['/antenna_log_' + label]
        #     except:
        #         pass

        for label in meta_data.keys():
            if len(logs[logs['Station'] == label]) > 0:
                antenna_dict[label] = logs[logs['Station'] == label]['Date']

        store.close()

        return antenna_dict


    @classmethod
    def downloadFullDataset(cls, out_file = 'pbo_data.h5', use_file=None):
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

            # Get filename for acc data
            with urlopen('https://www.unavco.org/data/gps-gnss/derived-products/derived-products.html') as url_handle:
                data = url_handle.read().decode()

            pattern = '<a href=\"(.*)\"\>MIT ACC Ancillary Files \(updated quarterly\)\<\/a\>'

            acc_url = 'https://www.unavco.org' + re.search(pattern,data).group(1)
            acc_filename =  acc_url.split('/')[-1]


            with open(acc_filename, 'wb') as acc_file:
                copyfileobj(urlopen(acc_url), acc_file)

            print("Download complete")
            
        else:
            filename = os.path.join(use_file, 'pbo.nam08.pos.tar.gz')

            filelist = glob(os.path.join(use_file,'*'))

            acc_filename = None
            for name in filelist:
                if re.search('MIT_ACC_Ancillary_Files_', name):
                    acc_filename=name

            if acc_filename == None:
                raise FileNotFoundError('No Ancillary file found')

        print('Parsing data')


        tar = tarfile.open(filename)
        store = pd.HDFStore(out_file, complib='zlib', complevel=5)


        member_list = [member for member in tar.getmembers() if member.name[-3:] == 'pos']
        names = list()
        meta_data = defaultdict(list)

        for info in tqdm(member_list):
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


        # Parse ancillary information
        def to_datetime(input_data):
            row = input_data[1]
            year = row['Year']
            month = row['Month']
            day = row['Day']
            hour = row['Hour']
            minute = row['Minute']

            return pd.to_datetime(pd.datetime(year,month,day,hour,minute))

        with ZipFile(acc_filename) as zipfile:
            # Find antenna and read information
            anttext = None
            for zip_info in zipfile.filelist:
                if re.search('All_PBO_ants.eq$', zip_info.filename):
                    anttext = zipfile.read(zip_info).decode()
                    break

            if anttext == None:
                raise RuntimeError('Cannot find antenna information!')
            # Convert comment characters to a standard comment character
            anttext_comment = re.sub('[*!]','#',anttext)

            comments = []
            for line in anttext.splitlines():
                parse = re.search('\! (.*)', line)
                if parse:
                    parse.group(1)
                    comments.append(parse.group(1))

            antio = io.StringIO(anttext_comment)
            antdata = pd.read_table(antio,comment='#',header=None,sep='\s+',skipinitialspace=True,skip_blank_lines=True,
                                 engine='python', names=['Command','Station','New_Name','Year','Month','Day','Hour','Minute'])
            antdata['Date'] = list(map( to_datetime, antdata.iterrows() ))
            antdata['Comment'] = comments        

            store.put('antenna_logs', antdata)
        
        store.close()

        cls.setDataLocation( 'pbo', os.path.abspath(out_file) )
