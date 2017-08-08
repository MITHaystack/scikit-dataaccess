from skdaccess.framework.data_class import DataFetcherStorage, TableWrapper


from collections import OrderedDict
import pandas as pd
import numpy as np
import pyproj

class DataFetcher(DataFetcherStorage):
    ''' 
    Fetches data for the Interactive Multisensor Snow and Ice Mapping System Daily Northern Hemisphere Snow and Ice Analysis
    '''

    def __init__(self, coordinate_dict, start_date, end_date):
        '''
        Intializes the Data Fetcher

        @param coordinate_dict: Dictionary of locations where the names are the keys and the items are
                                lists containing the latitude and longitude are the values
        @param start_date: Starting date
        @param end_date: Ending date
        '''

        super(DataFetcher, self).__init__([])

        self.coordinate_dict = coordinate_dict
        self.start_date = start_date
        self.end_date = end_date

    def output(self):
        '''
        Fetch snow coverage data for coordinates

        @return Data wrapper for snow coverage
        '''

        data_file    = DataFetcher.getDataLocation('imsdnhs')
        if data_file is None:
            print("No data available")
            return None

        

        store = pd.HDFStore(data_file)

        # Projection information
        x_start = -12288000.0
        x_end = 12288000.0
        y_start = 12288000.0
        y_end = -12288000.0
        x_dim = 6144
        y_dim = 6144
        x_inc = (x_end - x_start) / x_dim
        y_inc = (y_end - y_start) / y_dim
        proj = pyproj.Proj('+proj=stere +lat_0=90 +lat_ts=60 +lon_0=-80 +k=1 +x_0=0 +y_0=0 +ellps=WGS84 +datum=WGS84 +units=m +no_defs')

        # Function that determines the x,y image coordinate for a
        # given (latitude, longitude) pair
        def convertToXY(lat, lon):
            ux, uy = proj(lon,lat)
            x = np.round(((ux - x_start) / x_inc) - 0.5).astype(np.int)
            y = np.round(((uy - y_start) / y_inc) - 0.5).astype(np.int)
            return (x,y)


        label_list = []
        lat_array = np.zeros(len(self.coordinate_dict),dtype=np.float)
        lon_array = np.zeros(len(self.coordinate_dict),dtype=np.float)

        for i, (label, coordinates) in enumerate(self.coordinate_dict.items()):
            label_list.append(label)
            lat_array[i] = coordinates[0]
            lon_array[i] = coordinates[1]
            

        x_array,y_array = convertToXY(lat_array, lon_array)

        # # Forming a complex number to remove duplicate
        # # coordinates
        # complex_array = np.unique(x_array * 1j * y_array)

        # x_array = complex_array.real
        # y_array = complex_array.imag


        
        data_dict = OrderedDict()
        for label,x,y  in zip(label_list, x_array,y_array):
            data_dict[label] = pd.DataFrame({'Snow': store['y_' + str(y).zfill(4)].loc[:,x].reindex(pd.date_range(pd.to_datetime(self.start_date),
                                                                                                                  pd.to_datetime(self.end_date)),fill_value=-1)})

        return TableWrapper(data_dict, default_columns = ['Snow'])
            
