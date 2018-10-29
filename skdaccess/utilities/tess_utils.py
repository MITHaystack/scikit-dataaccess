# Standard library imports
from collections import OrderedDict

# Third party imports
from astropy.table import Table

def parseTessData(fits_data):
    """
    Retrieve Tess lightcurve data from astropy.io.fits.HDUList object

    @param fits_data: astropy.io.fits.HDUList object that corresponding to a Tess lightcurve fits file
    @return Pandas data frame of light curve, ordered dictionary of metadata
    """

    metadata_dict = OrderedDict()

    metadata_dict["Primary"] = fits_data[0].header
    metadata_dict["Lightcurve"] = fits_data[1].header



    return Table(fits_data[1].data).to_pandas(), metadata_dict
