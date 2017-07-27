import numpy as np

def normalize(in_data, column='PDCSAP_FLUX', group_column='QUARTER'):
    '''
    This function normalizes PDCSAP_FLUX data by quarter by dividing the flux by the median for the quarter

    @param in_data: Data to be normalized
    @param column: Name of column to be normalized
    @param group_column: Name of column used to group data
    '''

    if group_column != None:
        group_list = list(set(in_data[group_column]))

        group_list.sort()

        for group in group_list:
            index = in_data[group_column] == group
            in_data.loc[index, column] = in_data.loc[index,column] / np.nanmedian(in_data.loc[index,column])
