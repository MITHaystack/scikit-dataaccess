# 3rd party import
from tqdm import tqdm


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
