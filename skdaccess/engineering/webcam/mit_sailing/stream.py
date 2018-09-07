# The MIT License (MIT)
# Copyright (c) 2018 Massachusetts Institute of Technology
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


# Skdaccess imports
from skdaccess.framework.data_class import DataFetcherStream, ImageWrapper
from skdaccess.framework.param_class import *


# Standard library imports
from collections import OrderedDict


class DataFetcher(DataFetcherStream):
    """
    Data Fetcher for retrieving webcam images from the MIT Sailing Pavilion
    """

    def __init__(self, camera_list = ['E','SE','SW','W']):
        """
        @param camera_list: Which camera to retrieve from (List that contains one or more of the following: 'E', 'SE', 'SW', or 'W')
        """
        self.camera_list = camera_list

        for camera in camera_list:
            if camera not in ['E','SE','SW','W']:
                raise RuntimeError('Camera: "' + camera + '" not understood')
        
        
        self._base_url  = 'http://sailing.mit.edu/img/'

        self._image_name = '/latest.jpg'

        super(DataFetcher, self).__init__()


    def output(self):
        """

        Retrieve data from webcams at the MIT Sailing Pavilion

        @return Image Wrapper containing the latest images from the webcams
        """

        url_list = []
        for camera in self.camera_list:
            url_list.append(self._base_url + camera + self._image_name)

        metadata, data = self.retrieveOnlineData(url_list)

        return ImageWrapper(data, meta_data = metadata)
