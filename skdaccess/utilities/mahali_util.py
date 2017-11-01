# The MIT License (MIT)
# Copyright (c) 2017 Massachusetts Institute of Technology
#
# Authors: Cody Rude
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


# 3rd party package imports
import pandas as pd

def convert_date(in_date):
    '''
    Converts input string to pandas date time, ignores other types of objects

    @param in_date: Input date

    return pandas data time object
    '''
    if isinstance(in_date,str):
        try:
            return pd.to_datetime(in_date)
        except ValueError as e:
            return pd.to_datetime(in_date, format='%Y%j')

    else:
        return in_date


def parseIonoFile(in_file, compression='infer'):
    iono_columns = ( "day",
                     "year",
                     "rec_latitude",
                     "rec_longitude",
                     "los_tec",
                     "los_tec_err",
                     "vertical_tec",
                     "azimuth",
                     "elevation",
                     "mapping_function",
                     "pp_latitude",
                     "pp_longitude",
                     "satellite",
                     "site",
                     "recBias",
                     "recBiasErr" )

    data =  pd.read_table(in_file,header=None, sep='\s+',
                          names=iono_columns,
                          compression=compression)

    data['time'] = pd.to_datetime(data.loc[:,'year'].apply(str) + '-01-01') \
                   + pd.to_timedelta(data.iloc[:,0],unit='day')



    data.set_index('time', inplace=True)
    data.sort_index(inplace=True)

    return data
