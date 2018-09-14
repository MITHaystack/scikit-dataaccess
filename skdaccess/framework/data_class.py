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

# """@package DataClass
# Provides base data classes inherited by the specific data fetchers
# """

# Standard library imports
import os
import pathlib
from glob import glob
from urllib import request, parse
import shutil
from collections import OrderedDict
import warnings
from urllib.request import HTTPPasswordMgrWithDefaultRealm
from urllib.request import HTTPBasicAuthHandler
from urllib.request import HTTPCookieProcessor
from urllib.request import build_opener, install_opener, urlopen
from io import BytesIO
from http.cookiejar import CookieJar
import fcntl
import struct


# Compatability imports for standard library
from six.moves import configparser
from six.moves.configparser import NoOptionError, NoSectionError

# 3rd party imports
from tqdm import tqdm
from skimage.io import imread
from astropy.io import fits
from atomicwrites import atomic_write
import requests


class DataFetcherBase(object):
    '''
    Base class for all data fetchers
    '''
    def __init__(self, ap_paramList=[], verbose=False):
        '''
        Initialize data fetcher with parameter list

        @param ap_paramList: List of parameters
        @param verbose: Output extra information
        '''

        self.ap_paramList = ap_paramList
        self.verbose = verbose

    def output(self):
        '''
        Output data wrapper

        @return Datawrapper
        '''
        pass

    def perturb(self):
        '''Perturb parameters'''
        for param in self.ap_paramList:
            param.perturb()

    def reset(self):
        '''Set all parameters to initial value'''
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

    def getConfig():
        '''
        Retrieve skdaccess configuration

        @return configParser.ConfigParser object of configuration
        '''

        config_location = os.path.join(os.path.expanduser('~'), '.skdaccess.conf')

        conf = configparser.ConfigParser()
        conf.read(config_location)

        return conf

    def getConfigItem(section, key):
        """
        Retrieve skdaccess configuration item

        @param section: Section of configuration item
        @param key: Configuration key value
        @return Requested configuration item or None if it doesn't exist
        """

        conf = DataFetcherBase.getConfig()
        if section in conf:
            return conf.get(section, key, fallback=None)
        else:
            return None

    def writeConfigItem(section, key, value):
        """
        Retrieve skdaccess configuration item

        @param section: Section of configuration item
        @param key: Configuration key value
        @return Requested configuration item or None if it doesn't exist
        """
        conf = DataFetcherBase.getConfig()

        if section not in conf:
            conf.add_section(section)

        conf.set(section, key, value)
        DataFetcherBase.writeConfig(conf)

    def writeConfig(conf):
        '''
        Write config to disk

        @param conf: configparser.ConfigParser object
        '''
        config_location = os.path.join(os.path.expanduser('~'), '.skdaccess.conf')
        config_handle = open(config_location, "w")
        conf.write(config_handle)
        config_handle.close()

    def multirun_enabled(self):
        '''
        Returns whether or not this data fetcher is multirun enabled.

        @return Boolean indicating whether or not this data fetcher is multirun enabled
        '''
        pass

    def verbose_print(self, *args, **kwargs):
        """
        Print statement if verbose flag is set

        @param *args: Arguments to pass to print
        @param **kwargs: Keyword arguments to pass to print
        """
        if self.verbose:
            print(*args, **kwargs)

class DataFetcherLocal(DataFetcherBase):
    ''' Data fetcher base class for use when storing data locally'''
    def getDataLocation(data_name):
        '''
        Get the location of data set

        @param data_name: Name of data set

        @return string of data location, None if not found
        '''
        data_name = str.lower(data_name)

        conf = DataFetcherLocal.getConfig()
        try:
            return conf.get(data_name, 'data_location')
        except (NoOptionError, NoSectionError):

            # If it doesn't exist, create a new one

            # Check if an alternate root has been defined
            try:
                data_location = os.path.join(conf.get('skdaccess', 'root'), data_name)
            except (NoOptionError, NoSectionError):
                data_location = os.path.join(os.path.expanduser('~'), '.skdaccess', data_name)

            # Make directory and set location
            os.makedirs(data_location, exist_ok=True)
            DataFetcherLocal.setDataLocation(data_name, data_location)

            return data_location

    def setDataLocation(data_name, location, key='data_location'):
        '''
        Set the location of a data set

        @param data_name: Name of data set
        @param location: Location of data set
        @param key: Key of configuration option
        '''

        conf = DataFetcherLocal.getConfig()


        if not conf.has_section(data_name):
            conf.add_section(data_name)

        conf.set(data_name, key, location)
        DataFetcherLocal.writeConfig(conf)


class DataFetcherStorage(DataFetcherLocal):
    ''' Data fetcher base class for use when entire data set is downloaded'''
    @classmethod
    def downloadFullDataset(cls, out_file, use_file=None):
        '''
        Abstract function used to download full data set

        @param out_file: output file name
        @param use_file: Use previously downloaded data

        @return Absolute path of parsed data
        '''
        pass

    def multirun_enabled(self):
        '''
        Returns whether or not this data fetcher is multirun enabled.

        @return Boolean indicating whether or not this data fetcher is multirun enabled
        '''
        return True

class DataFetcherStream(DataFetcherBase):
    '''
    Data fetcher base class for downloading data into memory
    '''
    def retrieveOnlineData(self, data_specification):
        '''
        Method for downloading data into memory

        @param data_specification: Url list of data to be retrieved

        @return Retrieved data
        '''

        # Dictionary to store results
        data_dict = OrderedDict()
        metadata_dict = OrderedDict()


        # Parse data
        for url in data_specification:

            # Get http data type
            with urlopen(url) as url_access:
                content_type = url_access.info().get_content_type()

                # Access fits file
                if content_type == 'application/fits':

                    # Do not want caching to avoid issues when running multiple pipelines
                    bytes_data = BytesIO(url_access.read())
                    with warnings.catch_warnings(), fits.open(bytes_data, cache=False) as hdu_list:
                        warnings.simplefilter("ignore", fits.verify.VerifyWarning)

                        # Need to fix header otherwise astropy can fail to read data
                        hdu_list.verify('fix')

                        data_dict[url] = hdu_list[1].data
                        metadata_dict[url] = hdu_list[1].header

                # Access jpg file
                elif content_type == 'image/jpeg':
                    data_dict[url] = imread(url)
                    metadata_dict[url] = None

                # Throw warning if content_type not understood
                else:
                    raise RuntimeError('Did not understand content type: ' + content_type)

        return metadata_dict, data_dict


    def multirun_enabled(self):
        '''
        Returns whether or not this data fetcher is multirun enabled.

        @return Boolean indicating whether or not this data fetcher is multirun enabled
        '''
        return True


class DataFetcherCache(DataFetcherLocal):
    '''
    Data fetcher base class for downloading data and caching results on hard disk
    '''

    def checkIfDataExists(self, in_file_name):
        '''
        Checks if the file exists on the filesystem and the file is not empty

        @param in_file_name: Input filename to test
        @return True if data exists and False otherwise
        '''
        try:
            with open(in_file_name, 'rb') as read_file:
                rv = fcntl.fcntl(read_file, fcntl.LOCK_SH)
                first_byte = read_file.read(1)

            if len(first_byte) == 0:
                return False
            else:
                return True

        except FileNotFoundError:
            return False

    def cacheData(self, keyname, online_path_list, username=None, password=None, authentication_url=None,
                  cookiejar = None, use_requests=False, use_progress_bar=True):
        '''
        Download and store specified data to local disk

        @param keyname: Name of dataset in configuration file
        @param online_path_list: List of urls to data
        @param username: Username for accessing online resources
        @param password: Password for accessing online resources
        @param authentication_url: The url used for authentication (unused when use_requests=True)
        @param cookiejar: The cookiejar that stores credentials (unused when use_requests=True)
        @param use_requests: Use the requests library instead of the standard library for accessing resources
        @param use_progress_bar: Use a progress bar to show number of items downloaded

        @return List of downloaded file locations
        '''

        def parseURL(data_location, in_path):
            '''
            This function takes the file path of saved data and determines
            what url created it.

            @param data_location: Absolute path to root directory whose path is not part of the url
            @param path: Path to object that will be used to generate a url

            @return ParseResult of url generated from in_path
            '''
            data_location_parts = len(pathlib.Path(data_location).parts[:])
            path = pathlib.Path(in_path)
            access_type = path.parts[data_location_parts]
            if access_type != 'file':
                access_type += '://'
            else:
                access_type += ':///'

            url_path = pathlib.Path(*path.parts[data_location_parts+1:]).as_posix()
            return parse.urlparse(access_type+url_path)

        def generatePath(data_location, parsed_url):
            '''
            This function takes a parsed url (ParseResult) and
            generates the filepath to where the data should be stored
            stored

            @param data_location: Location where data is stored
            @param parsed_url: ParseResult generated from url

            @return Local path to file
            '''

            if parsed_url.query == '':
                return os.path.join(data_location, parsed_url.scheme,parsed_url.netloc, parsed_url.path[1:])

            else:
                return os.path.join(data_location, parsed_url.scheme,parsed_url.netloc,
                                    parsed_url.path[1:] + '?' + parsed_url.query)

        # Get absolute path to data directory
        data_location = DataFetcherCache.getDataLocation(keyname)

        # If it doesn't exist, create a new one
        if data_location == None:
            data_location = os.path.join(os.path.expanduser('~'), '.skdaccess',keyname)
            os.makedirs(data_location, exist_ok=True)
            DataFetcherCache.setDataLocation(keyname, data_location)

        # Get currently downloaded files
        downloaded_full_file_paths = [filename for filename in glob(os.path.join(data_location,'**'), recursive=True) if os.path.isfile(filename)]
        # Remove files empty files
        downloaded_full_file_paths = [filename for filename in downloaded_full_file_paths if self.checkIfDataExists(filename)]
        # Convert filenames to urls
        downloaded_parsed_urls = set(parseURL(data_location, file_path) for file_path in downloaded_full_file_paths)


        # Determine which files are missing
        parsed_http_paths = [parse.urlparse(online_path) for online_path in online_path_list]
        missing_files = list(set(parsed_http_paths).difference(downloaded_parsed_urls))

        missing_files.sort()

        # Download missing files
        if len(missing_files) > 0:
            # Sanity check on input options
            if use_requests == True and authentication_url != None:
                raise ValueError('Cannot use an authentication url with requests')


            # Setup connection (non requests)
            if not use_requests:
                # Deal with password protected urls
                # This method comes from
                # https://wiki.earthdata.nasa.gov/display/EL/How+To+Access+Data+With+Python
                if username != None or password != None:
                    password_manager = HTTPPasswordMgrWithDefaultRealm()
                    if authentication_url == None:
                        authentication_url = [parsed_url.geturl() for parsed_url in missing_files]
                    password_manager.add_password(None, authentication_url, username, password)
                    handler = HTTPBasicAuthHandler(password_manager)

                    # If no cookiejar was given, create a new one
                    if cookiejar == None:
                        cookiejar = CookieJar()

                    cookie_processor = HTTPCookieProcessor(cookiejar)

                    install_opener(build_opener(cookie_processor, handler))

                # Use a cookie with no username or password
                elif cookiejar != None:
                    cookie_processor = HTTPCookieProcessor(cookiejar)
                    install_opener(build_opener(cookie_processor))


            if use_progress_bar:
                missing_files_loop = tqdm(missing_files)
            else:
                missing_files_loop = missing_files

            for parsed_url in missing_files_loop:
                out_filename = generatePath(data_location, parsed_url)
                os.makedirs(os.path.split(out_filename)[0],exist_ok=True)

                with open(out_filename, 'a+b') as lockfile:

                    fcntl.lockf(lockfile, fcntl.LOCK_EX)
                    lockfile.seek(0)
                    if len(lockfile.read(1)) == 0:

                        with atomic_write(out_filename, mode='wb', overwrite=True) as data_file:
                            if not use_requests:
                                shutil.copyfileobj(urlopen(parsed_url.geturl()), data_file)
                            else:
                                if username != None or password != None:
                                    # This method to download password protected data comes from
                                    # https://wiki.earthdata.nasa.gov/display/EL/How+To+Access+Data+With+Python
                                    with requests.Session() as session:
                                        initial_request = session.request('get',parsed_url.geturl())
                                        r = session.get(initial_request.url, auth=(username,password), stream=True)

                                        if r.status_code == 401:
                                            raise RuntimeError("Authorization Denied")

                                        shutil.copyfileobj(r.raw, data_file, 1024*1024*10)
                                else:
                                    with requests.Session() as session:
                                        r = session.get(parsed_url.geturl(), stream=True)
                                        shutil.copyfileobj(r.raw, data_file, 1024*1024*10)


        # Return a list of file locations for parsing
        return [generatePath(data_location, parsed_url) for parsed_url in parsed_http_paths]


    def multirun_enabled(self):
        '''
        Returns whether or not this data fetcher is multirun enabled.

        @return Boolean indicating whether or not this data fetcher is multirun enabled
        '''
        return False

    def getHDFStorage(self, keyname):
        """
        Retrieve a Pandas HDF Store for a dataset

        @param keyname: Key name of HDF store

        @return Pandas HDF Store
        """

        data_location = DataFetcherCache.getDataLocation(keyname)
        if data_location == None:
            data_location = os.path.join(os.path.expanduser('~'),'.skdaccess',keyname)
            os.makedirs(data_location, exist_ok=True)
            data_location = os.path.join(data_location, keyname + '_data.h5')
            DataFetcher.setDataLocation(keyname, data_location)

        return pd.HDFStore(data_location)



class DataWrapperBase(object):
    ''' Base class for wrapping data for use in DiscoveryPipeline '''

    def __init__(self, obj_wrap, run_id = -1, meta_data = None):
        '''
        Construct wrapper from input data.

        @param obj_wrap: Data to be wrapped
        @param run_id: ID of the run
        @param meta_data: Metadata to store with data
        '''

        self.data = obj_wrap
        self.results = dict()
        self.constants = dict()
        self.run_id = run_id
        self.meta_data = meta_data


    def update(self, obj):
        '''
        Updated wrapped data

        @param obj: New data for wrapper
        '''
        self.data = obj

    def updateMetadata(self, new_metadata):
        '''
        Update metadata

        @param new_metadata: New metadata
        '''
        self.meta_data = new_metadata

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
        Add a result to the data wrapper

        @param rkey: Result key
        @param rres: Result
        '''
        self.results[rkey] = rres

    def reset(self):
        ''' Reset data back to original state '''
        self.results = dict()

    def info(self, key=None):
        '''
        Get information about data wrapper

        @return The stored metadata
        '''
        if key==None:
            return self.meta_data
        else:
            return self.meta_data[key]

    def getIterator(self):
        '''
        Get an iterator to the data

        @return iterator to data
        '''
        pass

    def __len__(self):
        '''
        Get length of wrapped data

        @return length of wrapped data
        '''

        return len(self.data)

    def getRunID(self):
        '''
        Get the Run ID

        @return run_id
        '''
        return self.run_id



class SeriesWrapper(DataWrapperBase):
    '''
    Data wrapper for series data using a data panel
    '''

    def __init__(self, obj_wrap, data_names, error_names = None, meta_data = None, run_id = -1):
        '''
        Initialize Series Wrapper

        @param obj_wrap: Pandas data panel to wrap
        @param data_names: List of data column names
        @param error_names: List of error column names
        @param meta_data: Metadata
        @param run_id: ID of run
        '''


        self.data_names = data_names
        self.error_names = error_names

        super(SeriesWrapper, self).__init__(obj_wrap, run_id, meta_data)

    def getIterator(self):
        '''
        Get an iterator to the data

        @return Iterator (label, data, errors) that will cycle over data and error names
        '''

        if self.error_names != None:

            for frame in self.data.minor_axis:
                for data_index,error_index in zip(self.data_names, self.error_names):
                    yield data_index, self.data.loc[data_index, :, frame], self.data.loc[error_index, :, frame]

        else:
            for frame in self.data.minor_axis:
                for data_index in self.data_names:
                    yield data_index, self.data.loc[data_index, :, frame], None



    def getIndices(self):
        '''
        Get the indicies of the data

        @return index of data
        '''

        return (list(self.data.minor_axis), self.data_names)


    def getLength(self):
        '''
        Get total number of series that the iterate will loop over

        @return Number of series iterator will traverse over
        '''
        return self.data.shape[2]*len(self.data_names)

class SeriesDictionaryWrapper(SeriesWrapper):
    '''
    Data wrapper for series data using a dictionary of data frames
    '''

    def getIterator(self):
        '''
        Get an iterator to the data

        @return Iterator (label, data, errors) that will cycle over data and error names
        '''

        if self.error_names != None:

            for frame in self.data.keys():
                for data_index,error_index in zip(self.data_names, self.error_names):
                    yield data_index, self.data[frame].loc[:, data_index], self.data[frame].loc[:, error_index]

        else:
            for frame in self.data.keys():
                for data_index in self.data_names:
                    yield data_index, self.data[frame].loc[:, data_index], None


    def getIndices(self):
        '''
        Get the indices of the data

        @return index of data
        '''

        return (list(self.data.keys()), self.data_names)


    def getLength(self):
        '''
        Get total number of series that the iterate will loop over

        @return Number of series iterator will traverse over
        '''

        return len(self.data) * len(self.data_names)


class TableWrapper(DataWrapperBase):
    '''
    Data wrapper for table data using an ordered dictionary
    '''
    def __init__(self, obj_wrap, run_id = -1, meta_data = None, default_columns = None, default_error_columns = None):
        '''
        Construct object from input data.

        @param obj_wrap: Data to be wrapped
        @param run_id: ID of the run
        @param meta_data: Metadata to store with data
        @param default_columns: Default columns for pipeline items
        @param default_error_columns: Default error columns for pipeline items
        '''
        self.default_columns = default_columns
        self.default_error_columns = default_error_columns
        super(TableWrapper, self).__init__(obj_wrap, run_id, meta_data)

    def getIterator(self):
        '''
        Iterator access to data.

        @return iterator to (label, data frame) from Dictionary
        '''
        for label,frame in self.data.items():
            yield label,frame

    def getLength(self):
        '''
        Get number of data frames

        @return Number of data frames
        '''
        return len(self.data)

    def updateData(self, label, index, column_names, new_data):
        '''
        Update wrapped data

        @param label: Data label
        @param index: Index of data to update
        @param column_names: Names of columns to update
        @param new_data: Data to replace the old data
        '''

        self.data[label].loc[index, column_names] = new_data

    def addColumn(self, label, column_names, new_data):
        '''
        Add new column to data

        @param label: Data label
        @param column_names: Names of columns to update
        @param new_data: New data to add
        '''

        self.data[label].loc[:,column_names] = new_data

    def getDefaultColumns(self):
        '''
        Get the default columns of data

        @return List of default columns
        '''
        return self.default_columns

    def getDefaultErrorColumns(self):
        '''
        Get the default error columns of data

        @return List of default error columns
        '''
        return self.default_error_columns

    def removeFrames(self,label_list):
        '''
        Remove Data Frames from wrapper

        @param label_list: List of labels to remove
        '''

        for label in label_list:
            del self.data[label]

    def updateFrames(self,label_list,frame_list):
        '''
        Update data frames

        @param label_list: List of labels to update
        @param frame_list: List of updated frames
        '''
        for label, frame in zip(label_list, frame_list):
            self.data[label] = frame

class ImageWrapper(DataWrapperBase):
    '''
    Wrapper for image data
    '''

    def getIterator(self):
        '''
        Get an iterator to the data

        @return Iterator yielding (label, image_data)
        '''

        return iter(self.data.items())


    def updateData(self, label, new_data):
        '''
        Change image

        @param label: Label of data to be changed
        @param new_data: New data to replace old data
        '''

        self.data[label] = new_data


    def deleteData(self, label):
        '''
        Delete image

        @param label: Delete image with label
        '''
        del self.data[label]

class XArrayWrapper(DataWrapperBase):
    '''
    Wrapper for xarrays
    '''
    def __init__(self, obj_wrap, index_list, run_id = -1 ):

        self.index_list = index_list

        super(XArrayWrapper, self).__init__(obj_wrap, run_id)


    def getIterator(self):
        '''
        Get an iterator that iterators over the index

        @return iterator to data
        '''

        for index in self.index_list:
            yield index, self.data[index]


    def info(self, key=None):
        '''
        Get information about xarray data wrapper

        @return The stored metadata
        '''

        if key==None:
            return self.data.attrs
        else:
            return self.data[key].attrs
