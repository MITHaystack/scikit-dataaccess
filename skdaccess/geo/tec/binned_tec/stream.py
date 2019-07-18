"""This module is used to access binned vertical total electron content data from the Madrigal database.

Calling output returns an iterator that will loop over binned TEC data from the start time to the end time,
of the end of data in the Madrigal database, which ever comes first.  next returns a tuple of (datetime,
pandas data frame where the 2D data is vertical TEC, the row indices are the latitudes, and the columns are the
longitudes

Written by Bill Rideout brideout@mit.edu

$Id$
"""


# The MIT License (MIT)
# Copyright (c) 2018 Massachusetts Institute of Technology
#
# Author: Bill Rideout
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

# Standard library imports
import os
import datetime, time
import xmlrpc.client
import traceback
import random

# Scikit Data Access
import skdaccess.framework.data_class

# Third party packages
import pandas

class DataFetcher(skdaccess.framework.data_class.DataFetcherStream):

    """ Data Fetcher constructor for retrieving binned Vertical TEC.  This object is also an iterator
    over the Binned TEC data.  Iterator returns a tuple of (datetime, pandas data frame of vertical TEC
    values in TECu, columns = latitutes, rows = longitudes)"""

    def __init__(self, user_name, user_email, user_affiliation,
                 startDT, endDT,
                 startLat, endLat, stepLat,
                 startLon, endLon, stepLon,
                 serverUrl, serverPort,
                 fiveMinSteps=1, timeSteps=1):
        """
        @param user_name: user name (string)
        @param user_email: user email (string)
        @param user_affiliation: user affiliation (string)
        @param startDT - datetime.datetime to start data collection
        @param endDT - datetime.datetime to end iteration
        @param startLat - lower latitude to start at (-90 to 90, integer)
        @param endLat - upper latitude to end at (-90 to 90, integer)
        @param stepLat - latitude step (minimum 1, integer, (endLat - startLat) % stepLat must == 0)
        @param startLon - lower longitude to start at (-90 to 90, integer)
        @param endLon - upper longitude to end at (-90 to 90, integer)
        @param stepLon - longitude step (minimum 1, integer, (endLon - startLon) % stepLon must == 0)
        @param serverUrl - url to binned TEC server (string)
        @param serverPort - port of server (integer)
        @param fiveMinSteps: number of 5 minutes steps to median filter over (default=1, min=1, integer)
        @param timeSteps: number of time periods to increment each time. 1 (the default) is continuous data.
        
        @return: None
        """
        self.server = xmlrpc.client.ServerProxy('http://%s:%i' % (serverUrl, serverPort), allow_none=True, use_builtin_types=True)
        self.key = self.server.create(user_name, user_email, user_affiliation, startDT, endDT,
                                      startLat, endLat, stepLat, startLon, endLon, stepLon,
                                      fiveMinSteps, timeSteps)
        

        
    def __iter__(self):
        return(self)

    def __next__(self):
        """Iterator returns a tuple of (datetime, pandas data frame of vertical TEC
        values in TECu, columns = latitutes, rows = longitudes)
        """
        items = self.server.next(self.key)
        if items is None:
            raise StopIteration
        dt, data = items
        # get name of random temp file
        filename = '/tmp/%i.pickle' % (random.randint(1,1000000000))
        f = open(filename, 'wb')
        f.write(data)
        f.close()
        unpickled_df = pandas.read_pickle(filename)
        os.remove(filename)
        return((dt, unpickled_df))
        
