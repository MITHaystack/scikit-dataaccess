# Standard library imports
from collections import OrderedDict
import os

# 3rd party imports
import pandas as pd
from pkg_resources import resource_filename

from tqdm import tqdm


def retrieveCommonDatesHDF(support_data_filename, key_list, in_date_list):
    '''
    Get a list of all dates that have  data available

    @support_data_filename: Filename of support data
    @in_date_list: Input date list to check

    @return dictionary of dates with data
    '''

    valid_dates = OrderedDict()

    support_full_path = resource_filename('skdaccess',os.path.join('support',support_data_filename))

    for key in key_list:

        try:
            available_dates = pd.read_hdf(support_full_path, key)
        except KeyError:
            print('Unknown station:',key)

        common_dates = list(set(in_date_list).intersection(set(available_dates)))

        common_dates.sort()

        valid_dates[key] = common_dates

    return valid_dates


def progress_bar(in_iterable, total=None, enabled=True):
    '''
    Progess bar using tqdm

    @param in_iterable: Input iterable
    @param total: Total number of elements
    @param enabled: Enable progress bar
    '''

    if enabled==True:
        return tqdm(in_iterable, total=total)
    else:
        return in_iterable
