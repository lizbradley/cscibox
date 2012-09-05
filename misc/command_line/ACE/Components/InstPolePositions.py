"""
InstPolePositions.py

Copyright (c) 2006-2007 University of Colorado. All rights reserved.
"""

from ACE.Framework.Component import Component

import math

class InstPolePositions(Component):
    def __init__(self, collections, workflow):
        super(InstPolePositions, self).__init__(collections, workflow)
        self.values = collections.get("polepositions")
        self.keys = self.values.keys()
        self.keys.sort()

    def __call__(self, samples):
        for s in samples:
            age = int(s["age"])
            lat = s["latitude"]
            lon = s["longitude"]

            s["paleomagnetic latitude"] = self.get_paleomagnetic_latitude_for_age(age, lat, lon)

        return (([self.get_connection()], samples),)

    def get_paleomagnetic_latitude_for_age(self, age, lat, lon):
        if age <= 10000:
            return abs(self.get_interpolated_paleomagnetic_latitude(age, lat, lon))

        if age > 10000:
            return abs(lat)

    def get_interpolated_paleomagnetic_latitude(self, age, lat, lon):
        A    = None
        B    = None
        i    = 0
        while i < (len(self.keys) - 1):
            A = self.keys[i]
            B = self.keys[i+1]

            if ((A < age) and (age <= B)):
                break;

            i = i + 1

        A_age = A
        B_age = B

        A_lat = self.get_paleomagnetic_latitude(A_age, lat, lon)
        B_lat = self.get_paleomagnetic_latitude(B_age, lat, lon)

        lat_diff  = B_lat - A_lat
        age_diff  = B_age - A_age
        targ_diff = age - A_age

        div     = lat_diff / age_diff
        product = targ_diff * div

        return A_lat + product

    def get_paleomagnetic_latitude(self, age, lat, lon):
        # Implements the equation
        # 90 - ACOS(
        # SIN(ls/180*pi)*SIN(A/180*pi) +
        # COS(ls/180*pi)*COS(A/180*pi)*COS(B/180*pi-fs/180*pi)
        # )*180/pi
        # where
        # ls = lat
        # fs = lon
        # A = Holocene Lat (for age)
        # B = Holocene Long (for age)

        # define constants
        PI = math.pi

        # convert input values to radians
        geoLat = lat * PI / 180.0
        geoLon = lon * PI / 180.0
        hLat   = self.values[age]["latitude"] * PI / 180.0
        hLon   = self.values[age]["longitude"] * PI / 180.0

        # calculate sin and cosine values
        sinGeoLat     = math.sin(geoLat);
        cosGeoLat     = math.cos(geoLat);
        sinHLat       = math.sin(hLat);
        cosHLat       = math.cos(hLat);
        cosHLonGeoLon = math.cos(hLon - geoLon);

        # combine sin and cosine values
        sinProduct = sinGeoLat * sinHLat;
        cosProduct = cosGeoLat * cosHLat * cosHLonGeoLon;
        sincosSum  = sinProduct + cosProduct;
        acos       = math.acos(sincosSum);

        # perform final calculations
        acos = acos / PI * 180

        return 90.0 - acos;

# vim: ts=4:sw=4:et
