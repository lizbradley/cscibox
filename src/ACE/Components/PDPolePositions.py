"""
PDPolePositions.py

* Copyright (c) 2006-2009, University of Colorado.
* All rights reserved.
*
* Redistribution and use in source and binary forms, with or without
* modification, are permitted provided that the following conditions are met:
*     * Redistributions of source code must retain the above copyright
*       notice, this list of conditions and the following disclaimer.
*     * Redistributions in binary form must reproduce the above copyright
*       notice, this list of conditions and the following disclaimer in the
*       documentation and/or other materials provided with the distribution.
*     * Neither the name of the University of Colorado nor the
*       names of its contributors may be used to endorse or promote products
*       derived from this software without specific prior written permission.
*
* THIS SOFTWARE IS PROVIDED BY THE UNIVERSITY OF COLORADO ''AS IS'' AND ANY
* EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
* WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
* DISCLAIMED. IN NO EVENT SHALL THE UNIVERSITY OF COLORADO BE LIABLE FOR ANY
* DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
* (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
* LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
* ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
* (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
* SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

Returns the geolatitude of the present day

"""

from ACE.Framework.Component import Component

import math

class PDPolePositions(Component):
    def __init__(self, collections, workflow):
        super(PDPolePositions, self).__init__(collections, workflow)
        self.values = collections.get("Geomagnetic Polarity - Ohno Hamano 1992")
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
        return abs(self.get_interpolated_paleomagnetic_latitude(0.0, lat, lon))

    def get_interpolated_paleomagnetic_latitude(self, age, lat, lon):
        A_age = self.keys[0]
        B_age = self.keys[1]

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
