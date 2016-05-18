#!/usr/bin/env python3

# The MIT License (MIT)
# Copyright (c) 2015 Massachusetts Institute of Technology
#
# Author: David Blair
# This software is part of the NSF DIBBS Project "An Infrastructure for
# Computer Aided Discovery in Geoscience" , PI: V. Pankratius
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


"""@package map_util
A collection of map manipulation tools
"""

import numpy as np
import math


class Planet:
    """
    A class for storing variables about a planetary body

    @params name: The name of the planetary body
    """

    def __init__(self, name):
        if (name.lower() == "earth") or (name.lower() == "wgs84"):
            self.a = 6378137.0
            self.b = 6356752.3142
            self.e_sq = (self.a**2 - self.b**2)/(self.a**2)
        if name.lower() == "moon":
            self.a = 1738140.0
            self.b = 1735970.0
            #NB: The Moon is considered a sphere (e_sq = 0.0) by convention,
            #    although the true calculated value would be
            #    e_sq = 0.0024953633422124632
            self.e_sq = 0.0

        self.equator_1deg = np.pi*self.a/180
        self.avg_radius = np.mean((self.a,self.b))


    def get_lateraldist_array(self, ppd):
        """
        Get an array of the lateral size of 1/ppd of a degree of longitude at
        every 1/ppd of a degree of latitude. Results given in meters.

        Example: input of ppd = 1 for the body "Earth" results in an array 180
        cells long with lateraldist_array[90] = 111 (m).

        @params ppd: the number of pixels-per-degree-of-latitude; the resulting
                     array will therefore be (180*ppd) cells tall

        @returns lateraldist_array: an array of the size (in meters) of 1 degree of
                                    longitude at each 1/ppd-th of a degree of latitude
        """

        # Set up the parameters for the body (everything in meters)
        equator_1deg = np.pi * self.a/180

        # Set up the latitude array. Here we use np.linspace() instead of np.arange() because
        # we want to ensure that the resulting array has a length equal to the number of cells
        # of latitude in the dataset, and change the starting and ending values by (1/2)*(1/ppd)
        # so that each value is at the center-point of a cell in the dataset
        lat_array = np.linspace(-90 + (1/(2*ppd)),
                                90 - (1/(2*ppd)), num=(ppd*180), dtype=np.float)

        # Iterate over the latitudes & calculate the length of (1/ppd) degrees of longitude
        # at each one
        lateraldist_array = np.empty(len(lat_array))
        for i in range(len(lat_array)):

            spherical_approx = equator_1deg * np.cos(np.radians(lat_array[i]))
            ellipsoid_dist = spherical_approx / \
                             np.sqrt(1 - (self.e_sq * (np.sin(np.radians(lat_array[i])))**2))

            lateraldist_array[i] = ellipsoid_dist / ppd

            ###DEBUG
            #print("Spherical approximation at {0:3g}: {1:8g}".format(lat, spherical_approx))
            #print("  Ellipsoid calculation at {0:3g} degrees: {1:-12.2f}".format(lat, ellipsoid_dist))

        return lateraldist_array


def sanitize_latlon(lat_lon_tuple, ppd=1, start_from_90N=False):
    """
    Wraps around latitude & longitudes, including interpretation of points past
    the poles.

    @params lat_lon_tuple: (lat, lon), in either degrees or pixels
    @params ppd: pixels-per-degree
    @params start_from_90N: consider 90N to be 0 latitude
    """

    lat, lon = lat_lon_tuple

    if start_from_90N:
        if lat < 0:
            return [-lat, (lon + 180*ppd)%(360*ppd)]
        elif lat > 180*ppd:
            return [-360*ppd - lat, (lon + 180*ppd)%(360*ppd)]
        else:
            return [lat, lon%(360*ppd)]
    else:
        if lat > 90*ppd:
            return [180*ppd - lat, (lon + 180*ppd)%(360*ppd)]
        elif lat < -90*ppd:
            return [-180*ppd - lat, (lon + 180*ppd)%(360*ppd)]
        else:
            return [lat, lon%(360*ppd)]


def trim_map(array, ppd, nswe, lat_npole=90, lon_offset=0):
    """
    Returns a copy of a map/array trimmed to the given N, S, W, E extents

    @params array: the input array to be trimmed
    @params ppd: the pixels-per-degree of the array
    @params nswe: a 1x4 array of the desired [N, S, W, E] edges
    @params lat_npole: the latitude of the N Pole in the same system as the
                          given N, S, W, E values
    @params lat_npole: the longitude of the prime meridian in the same system
                          as the given N, S, W, E values

    @returns trimmed_map: the input data trimmed to the desired edges
    """

    map_N = int((lat_npole - nswe[0])*ppd)
    map_S = int((lat_npole - nswe[1])*ppd)
    map_W = int((nswe[2] + lon_offset)*ppd)
    map_E = int((nswe[3] + lon_offset)*ppd)
    trimmed_map = array[map_N:map_S, map_W:map_E]

    return trimmed_map


def calc_slopes(topo_array, ppd, planet, scaled=True,
                nswe="global", lon_offset=0, lat_npole=90):
    """
    Calculate a slope map from a topographic dataset.

    For now, this tool assumes a global topographic dataset; in the future, it
    will be expanded to work on regional datasets as well. 

    @params topo_array: a global topographic dataset, in numpy array form
    @params ppd: the pixels-per-degree of the topo array
    @params bodyname: the name of the planetary body in question
    @params scaled: whether values should be scaled by latitude
    @params nswe: the (NW,SE) corners of the area-of-interest
    """

    # Parameters for different celestial bodies
    dist_1px_lat = (2 * np.pi * planet.avg_radius)/(360*ppd)

    ###DEBUG: OK
    #print("1/ppd of 1 degree around the lunar circumference:", 10921000 / 360 / ppd)
    #print("calculated as:", dist_1px_lat)

    # Calculate only part of the array?
    if nswe != "global":

        # Convert lat/lon values to pixel (cell) coordinates for slicing
        #N = (lat_npole - nswe[0])*ppd
        #S = (lat_npole - nswe[1])*ppd
        #W = (nswe[2] + lon_offset)*ppd
        #E = (nswe[3] + lon_offset)*ppd

        ###DEBUG
        #print(W,E,S,N)

        # Taking slice of data from [N:S, W:E]
        topo_array = trim_map(topo_array, ppd, nswe, lat_npole, lon_offset)

    # Get the array of the size of 1 pixel East-West at the ppd of the data. If
    # the data is non-global, trim the array to fit.
    lateraldist_array = planet.get_lateraldist_array(ppd)
    if nswe != "global":
        lateraldist_array = lateraldist_array[(lat_npole - nswe[0])*ppd:
                                              (lat_npole - nswe[1])*ppd]
        #lateraldist_array = lateraldist_array[N:S]

    ###DEBUG
    #print("max of lateraldist_array:", max(lateraldist_array))
    #print(lateraldist_array.shape)

    # Use np.gradient() to get the by-rows (North-South) and by-columns (East-West)
    # components of the slope very quickly
    S_slope, E_slope = np.gradient(topo_array)

    # Since numpy has no idea of the physical scale, though, we have to multiply
    # by something so that we have a distance/distance measurement. If we're
    # scaling with latitude, we can do this intelligently, otherwise we'll just
    # multiply by the distance along a great circle
    if scaled:
        E_slope = E_slope / lateraldist_array[:, np.newaxis]
        S_slope = S_slope / dist_1px_lat
    else:
        E_slope = E_slope / dist_1px_lat
        S_slope = S_slope / dist_1px_lat

    # Since each cell in the topo & slope arrays represents 1 pixel, and each
    # pixel represents a plane, the overall slope of that plane can be calculated
    # by taking the root of the sum of the squares of the slope components
    slope_array = np.sqrt(E_slope**2 + S_slope**2)
    # TODO: is this correct?

    # Calculate the aspect array (direction of the slope)
    aspect_array = np.degrees(np.arctan2(-E_slope, S_slope))

    # Go from dist/dist to degrees
    slope_array = np.degrees(np.arctan(slope_array))

    ###DEBUG:
    #f, [[ax1,ax4],[ax2,ax3]] = plt.subplots(2,2)
    #f1 = ax1.imshow(topo_array)
    #div1 = make_axes_locatable(ax1)
    #cax1 = div1.append_axes("right", size="15%", pad=0.1)
    #plt.colorbar(f1, cax=cax1)
    #f2 = ax2.imshow(E_slope, cmap="RdBu")
    #div2 = make_axes_locatable(ax2)
    #cax2 = div2.append_axes("right", size="15%", pad=0.1)
    #plt.colorbar(f2, cax=cax2)
    #f3 = ax3.imshow(S_slope, cmap="RdBu")
    #div3 = make_axes_locatable(ax3)
    #cax3 = div3.append_axes("right", size="15%", pad=0.1)
    #plt.colorbar(f3, cax=cax3)
    #f4 = ax4.imshow(aspect_array, cmap="gray")
    #div4 = make_axes_locatable(ax4)
    #cax4 = div4.append_axes("right", size="15%", pad=0.1)
    #plt.colorbar(f4, cax=cax4)

    return slope_array


# Vincenty distance adapted from public domain vincenty package:
# https://github.com/maurycyp/vincenty  
def wgs84_distance(point1, point2, planet=Planet("wgs84"), miles=False):
    """
    Vincenty's formula (inverse method) to calculate the distance (in
    kilometers or miles) between two points on the surface of a spheroid
    Doctests:
    >>> wgs84_distance((0.0, 0.0), (0.0, 0.0))  # coincident points
    0.0
    >>> wgs84_distance((0.0, 0.0), (0.0, 1.0))
    111.319491
    >>> wgs84_distance((0.0, 0.0), (1.0, 0.0))
    110.574389
    >>> wgs84_distance((0.0, 0.0), (0.5, 179.5))  # slow convergence
    19936.288579
    >>> wgs84_distance((0.0, 0.0), (0.5, 179.7))  # failure to converge
    >>> boston = (42.3541165, -71.0693514)
    >>> newyork = (40.7791472, -73.9680804)
    >>> wgs84_distance(boston, newyork)
    298.396057
    >>> wgs84_distance(boston, newyork, miles=True)
    185.414657
    """
    
    MILES_PER_KILOMETER = 0.621371
    MAX_ITERATIONS = 200
    CONVERGENCE_THRESHOLD = 1e-12  # .000,000,000,001

    a = planet.a
    b = planet.b
    f = 1 - b / a

    # short-circuit coincident points
    if point1[0] == point2[0] and point1[1] == point2[1]:
        return 0.0

    U1 = math.atan((1 - f) * math.tan(math.radians(point1[0])))
    U2 = math.atan((1 - f) * math.tan(math.radians(point2[0])))
    L = math.radians(point2[1] - point1[1])
    Lambda = L

    sinU1 = math.sin(U1)
    cosU1 = math.cos(U1)
    sinU2 = math.sin(U2)
    cosU2 = math.cos(U2)

    for iteration in range(MAX_ITERATIONS):
        sinLambda = math.sin(Lambda)
        cosLambda = math.cos(Lambda)
        sinSigma = math.sqrt((cosU2 * sinLambda) ** 2 +
                             (cosU1 * sinU2 - sinU1 * cosU2 * cosLambda) ** 2)
        if sinSigma == 0:
            return 0.0  # coincident points
        cosSigma = sinU1 * sinU2 + cosU1 * cosU2 * cosLambda
        sigma = math.atan2(sinSigma, cosSigma)
        sinAlpha = cosU1 * cosU2 * sinLambda / sinSigma
        cosSqAlpha = 1 - sinAlpha ** 2
        try:
            cos2SigmaM = cosSigma - 2 * sinU1 * sinU2 / cosSqAlpha
        except ZeroDivisionError:
            cos2SigmaM = 0
        C = f / 16 * cosSqAlpha * (4 + f * (4 - 3 * cosSqAlpha))
        LambdaPrev = Lambda
        Lambda = L + (1 - C) * f * sinAlpha * (sigma + C * sinSigma *
                                               (cos2SigmaM + C * cosSigma *
                                                (-1 + 2 * cos2SigmaM ** 2)))
        if abs(Lambda - LambdaPrev) < CONVERGENCE_THRESHOLD:
            break  # successful convergence
    else:
        return None  # failure to converge

    uSq = cosSqAlpha * (a ** 2 - b ** 2) / (b ** 2)
    A = 1 + uSq / 16384 * (4096 + uSq * (-768 + uSq * (320 - 175 * uSq)))
    B = uSq / 1024 * (256 + uSq * (-128 + uSq * (74 - 47 * uSq)))
    deltaSigma = B * sinSigma * (cos2SigmaM + B / 4 * (cosSigma *
                 (-1 + 2 * cos2SigmaM ** 2) - B / 6 * cos2SigmaM *
                 (-3 + 4 * sinSigma ** 2) * (-3 + 4 * cos2SigmaM ** 2)))
    s = b * A * (sigma - deltaSigma)

    s /= 1000  # meters to kilometers
    if miles:
        s *= MILES_PER_KILOMETER  # kilometers to miles

    return round(s, 6)
    
    

    

    

#### Test Examples #############################################################

# Testing sanitize_latlon
#print(sanitize_latlon((0,0)))
#print(sanitize_latlon((30,362)))
#print(sanitize_latlon((30,-40)))
#print(sanitize_latlon((92,0)))
#print()
#print(sanitize_latlon((-2,0), start_from_90N=True))
#print(sanitize_latlon((-2,-2), start_from_90N=True))
#print()
#ppd = 16
#print(sanitize_latlon((-2*ppd,0), ppd=ppd, start_from_90N=True))
#print(sanitize_latlon((-2*ppd, -2*ppd), ppd=ppd, start_from_90N=True))


#nw = [(90 - -42)*ppd, (345)*ppd]
#se = [(90 - -45)*ppd, (352)*ppd]
#topo_subset = data_array[nw[0]:se[0],nw[1]:se[1]]
#
#local_slope_map = calc_slopes(topo_subset, ppd)
#plt.imshow(local_slope_map, cmap="jet")
#plt.savefig("tycho.jpg")
#plt.show()


#ppd = int(topo_array.shape[0] / 180)
# Tycho
#nw = [131, 348]
#se = [135, 352]
#nwse = [nw,se]
# Tiny
#nw = [88, 178]
#se = [92, 182]
#nwse = [nw,se]
# Very large area
#nw = [10,90]
#se = [170,270]
#nwse = [nw,se]

#map1 = calc_slopes(topo_array, ppd, nwse=nwse, scaled=False)
#map2 = calc_slopes(topo_array, ppd, nwse=nwse, scaled=True)
