from skdaccess.geo.modis.cache import DataFetcher as MDF


class DataFetcher(MDF):

    '''
    Data fetcher for the modis surface reflectance product ('09', 1 km resolution)
    '''

    def __init__(self, ap_paramList, start_date, end_date, modis_platform = 'Terra',
                 daynightboth = 'D', grid=None, bands = [1,4,3]):
        '''
        Construct Data Fetcher for MODIS 1km surface reflectance
        
        @param ap_paramList[lat]: Search latitude
        @param ap_paramList[lon]: Search longitude
        @param start_date: Starting date
        @param end_date: Ending date
        @param modis_platform: Paltform (Either "Terra" or "Aqua")
        @param daynightboth: Use daytime data ('D'), nighttime data ('N') or both ('B')
        @param grid: Further divide each image into a multiple grids of size (y,x)
        @param bands: List of modis bands to retrieve
        '''

        
        available_bands = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]

        for band in bands:
            if band not in available_bands:
                raise ValueError('Band ' + str(band) + ' not available')
        
        index_list = ['1km Surface Reflectance Band ' + str(band) for band in bands]


        super(DataFetcher, self).__init__(ap_paramList, modis_platform, '09', index_list, start_date, end_date,
                                          daynightboth, grid)
        

