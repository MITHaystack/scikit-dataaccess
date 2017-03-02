#!/usr/bin/env python3

import argparse
import os
from skdaccess.utilities import data_util

def skdaccess_script():

    parser = argparse.ArgumentParser(description='The Sci-kit Data Access (skdaccess) package is a tool for integrating various scientific data sets into the Python environment using a common interface. This script can download different scientific data sets for offline analysis.')
    parser.add_argument('data_set', help='Name of data set', nargs='?')
    parser.add_argument('-l','--list', dest='list_bool', help='List data sets', action='store_true')
    parser.add_argument('-i','--input', dest='local_data', help='Use LOCAL_DATA that has already been downloaded')

    args = parser.parse_args()

    if args.list_bool:
        print("This utility can install one of the following data sets:")
        print()
        print('\tPBO - Plate Boundary Observatory GPS Time Series ')
        print('\tGRACE - Monthly Mass Grids')
        print('\tGroundwater - Ground water daily values from wells in California')
        parser.exit(1)

    if args.data_set is None:
        parser.print_help()
        parser.exit(1)

    final_path = None

    if str.lower(args.data_set) == 'pbo':
        final_path = data_util.downloadPBO(use_file=args.local_data)

    if str.lower(args.data_set) == 'grace':
        final_path = data_util.downloadGRACE(local_data=args.local_data)

    if str.lower(args.data_set) == 'groundwater':
        final_path = data_util.downloadGW(local_data=args.local_data)


    if final_path is not None:
        data_util.setDataLocation(str.lower(args.data_set), final_path)
    else:
        print('Data set unsupported')
