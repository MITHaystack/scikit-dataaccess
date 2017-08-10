import pandas as pd
import numpy as np

def combine_water_heights(in_data):
    '''
    Combine median and average water heights

    Create a column of water heights in input data frame using Median
    Water Depth by default, but fills in missing data using average
    values

    @param in_data: Input water heights data
    '''

    if 'Mean Water Depth' in in_data.columns and 'Median Water Depth' in in_data.columns:
        # replacing all null median data with mean data
        median_null_index = pd.isnull(in_data.loc[:,'Median Water Depth'])


        in_data.loc[:,'Combined Water Depth'] = in_data.loc[:,'Median Water Depth']

        # Check if there is any replacement data available
        if (~pd.isnull(in_data.loc[median_null_index, 'Mean Water Depth'])).sum() > 0:
            in_data.loc[median_null_index, 'Combined Water Depth'] = in_data.loc[median_null_index, 'Mean Water Depth']

    elif 'Mean Water Depth' in in_data.columns and 'Median Water Depth' not in in_data.columns:
        in_data.loc[:,'Combined Water Depth'] = in_data.loc[:,'Mean Water Depth']

    elif 'Mean Water Depth' not in in_data.columns and 'Median Water Depth' in in_data.columns:
        in_data.loc[:,'Combined Water Depth'] = in_data.loc[:,'Median Water Depth']

    else:
        raise ValueError("in_data needs either 'Mean Water Depth' or 'Median Water Depth' or both")


