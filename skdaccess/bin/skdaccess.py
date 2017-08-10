#!/usr/bin/env python3

import argparse
import os

from skdaccess.astro.kepler import DataFetcher as KDF
from skdaccess.geo.pbo import DataFetcher as PBODF
from skdaccess.geo.groundwater import DataFetcher as WDF
from skdaccess.geo.grace import DataFetcher as GRACEDF
from skdaccess.geo.gldas import DataFetcher as GLDASDF

def skdaccess_script():
    '''This funcion defines a script for downloading data'''
    parser = argparse.ArgumentParser(description='The Sci-kit Data Access (skdaccess) package is a tool for integrating various scientific data sets into the Python environment using a common interface. This script can download different scientific data sets for offline analysis.')
    parser.add_argument('data_set', help='Name of data set', nargs='?')
    parser.add_argument('-l','--list', dest='list_bool', help='List data sets', action='store_true')
    parser.add_argument('-i','--input', dest='local_data', help='Use LOCAL_DATA that has already been downloaded')
    parser.add_argument('-c','--check',dest='check_bool', help='Print data location for data set', action='store_true')

    args = parser.parse_args()

    if args.list_bool:
        print("This utility can install one of the following data sets:")
        print()
        print('\tPBO - Plate Boundary Observatory GPS Time Series ')
        print('\tGRACE - Monthly Mass Grids')
        print('\tGLDAS - Monthly estimates from GDLAS model in same resolution as GRACE')
        print('\tGroundwater - Ground water daily values from across the US')
        parser.exit(1)

    elif args.data_set is None:
        parser.print_help()
        parser.exit(1)


    elif args.check_bool:
        config = PBODF.getConfig()

        location = config.get(str.lower(args.data_set), 'data_location',fallback=None)

        if location == None:
            print('No data location available for ' + str.lower(args.data_set))
        else:
            print('The data is located at: ' + location)

        parser.exit(1)
        

    if str.lower(args.data_set) == 'pbo':
        PBODF.downloadFullDataset(use_file=args.local_data)

    elif str.lower(args.data_set) == 'grace':
        GRACEDF.downloadFullDataset(use_file=args.local_data)    

    elif str.lower(args.data_set) == 'gldas':
        GLDASDF.downloadFullDataset(use_file=args.local_data)        

    elif str.lower(args.data_set) == 'groundwater':
        WDF.downloadFullDataset(use_file=args.local_data)        

    else:
        print('Data set not understood')
