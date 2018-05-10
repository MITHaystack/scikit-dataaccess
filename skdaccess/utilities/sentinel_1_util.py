# Standard library imports
import xml.etree.ElementTree as ET

# 3rd party imports
import pandas as pd

def parseSatelliteData(in_satellite_file):
    '''
    Parse Sentinel satelllite data

    @param in_sentinel_file: Satellite orbit filename

    @return DataFrame of orbit information
    '''
    satellite_tree = ET.parse(in_satellite_file)

    names = ['TAI', 'UTC', 'UT1','Absolute_Orbit', 'X', 'Y', 'Z', 'VX', 'VY', 'VZ', 'Quality']
    time_converter = lambda x: pd.to_datetime(x[4:])
    converters = [time_converter, time_converter, time_converter, int, float, float, float,
                  float, float, float, lambda x: x]
    tmp_data = []

    for orbit in satellite_tree.findall('Data_Block/List_of_OSVs/OSV'):
        row = []
        for name, converter in zip(names, converters):
            row.append(converter(orbit.find(name).text))
        tmp_data.append(row)

    return pd.DataFrame(tmp_data, columns=names)
