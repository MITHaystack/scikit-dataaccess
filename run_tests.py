#!/usr/bin/env python3

# The MIT License (MIT)
# Copyright (c) 2017 Massachusetts Institute of Technology
# 
# Author: Cody Rude
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

import subprocess
from subprocess import check_call
import sys
import os
from glob import glob
from tempfile import TemporaryDirectory


from pkg_resources import resource_filename


command = 'python'
jupyter = 'jupyter'

directory = resource_filename('skdaccess', 'examples')
test_list = glob(os.path.join(directory,'*.ipynb'))

num_fails = 0

for test in test_list:
    with TemporaryDirectory() as tmpdir:
        try:
            print("Running:", test, end=' ', flush=True)
            res = check_call([jupyter,'nbconvert','--output=' + os.path.join(tmpdir, 'test_output'), '--ExecutePreprocessor.timeout=2000',
                              '--ExecutePreprocessor.enabled=True', test],
                             stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)

            print("... OK")
        except subprocess.CalledProcessError:
            print('... Failed')
            num_fails += 1


if num_fails == 0:
    print("all notebooks ran without errors")

else:
    if num_fails == 1:
        print("There was 1 failure")
    else:
        print("There were", num_fails, "failures")


