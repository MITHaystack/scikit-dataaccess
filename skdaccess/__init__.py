# The MIT License (MIT)
# Copyright (c) 2015 Massachusetts Institute of Technology
#
# Authors: Victor Pankratius, Justin Li, Cody Rude, David Blair, Michael Gowanlock
# This software is part of the NSF DIBBS Project "An Infrastructure for
# Computer Aided Discovery in Geoscience" (PI: V. Pankratius) and 
# NASA AIST Project "Computer-Aided Discovery of Earth Surface 
# Deformation Phenomena" (PI: V. Pankratius)
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

"""@package skdaccess
The scikit-dataaccess package (import as skdaccess) provides a common api
framework for importing and handling scientific data sets. This also supports
standardized metadata tags, annotations, and queries.

The package contains a base DataClass that provides a top level DataGenerator
and DataWrapper inherited by specific data sources. The DataGenerator parses
data, and the DataWrapper iterates over the data sources and returns desired
pieces of data.

Metadata Tags of the form:
#@meta key, value
"""

#@meta package, help


from . import *
import pkg_resources

# __version__ = pkg_resources.get_distribution('scikit-dataaccess').version
