"""
LalScalingFunctions.py

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

Scaling taken from Lal 1991 doi:10.1016/0012-821X(91)90220-C 
"""

from ACE.Framework.Component import Component
import math

class LalScalingFunctions(Component):
    def __init__(self, collections, workflow):
        super(LalScalingFunctions, self).__init__(collections, workflow)
        self.constants = collections.get("Constants")

        self.geolat = [0.0, 10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 90.0]
        self.a1 = [3.307E+02, 3.379E+02, 3.821E+02, 4.693E+02, 
                   5.256E+02, 5.711E+02, 5.634E+02, 5.634E+02]
        self.a2 = [2.559E+02, 2.521E+02, 2.721E+02, 3.946E+02,
                  5.054E+02, 5.881E+02, 6.218E+02, 6.218E+02]
        self.a3 = [9.843E+01, 1.110E+02, 1.325E+02, 9.776E+01,
                   1.420E+02, 1.709E+02, 1.773E+02, 1.773E+02]
        self.a4 = [2.050E+01, 2.073E+01, 2.483E+01, 4.720E+01,
                   5.887E+01, 7.612E+01, 7.891E+01, 7.891E+01]
        self.M  = [0.587, 0.600, 0.678, 0.833, 0.933, 1.00, 1.00, 1.00]
        
    def __call__(self, samples):
        for s in samples:
            self.setScalingFunctionSP(s)
            self.setScalingFunctionTH(s)
            self.setScalingFunctionMU(s)
            self.setScalingFunctionMUfast(s)

        return (([self.get_connection()], samples),)

    def setScalingFunctionSP(self, s):
        # Calculate the production rate according to table 2 of Lal 1991
        # for a particular geomagnetic latitude and elevation.
        # Divide this production rate by that at high latitude and sea level

        # Get appropriate coefficients for latitude
        
        lat = s["latitude"]

        a1_interp = self.get_interpolated_coefficient(self.geolat,self.a1,lat)
        a2_interp = self.get_interpolated_coefficient(self.geolat,self.a2,lat)
        a3_interp = self.get_interpolated_coefficient(self.geolat,self.a3,lat)
        a4_interp = self.get_interpolated_coefficient(self.geolat,self.a4,lat)

        elev = s["effective elevation"]/1000.0

        local_prod = a1_interp + a2_interp * elev + a3_interp * elev**2 + a4_interp * elev**3

        # Production rate at high latitude and sea level is given with 
        # a1_interp = self.get_interpolated_coefficient(self.geolat,self.a1,90)
        # a2_interp = ...
        # and elev = 0
        # This rate does not change with time and is equal to a1[7]

        s["S_sp"] = local_prod/self.a1[7]

    def setScalingFunctionTH(self, s):

        # No low energy neutrons, so use spallation 

        s["S_th"] = s["S_sp"]

    def setScalingFunctionMU(self, s):

        # Stone Equation 3 doi: 10.1029/2000JB900181
        lat = s["latitude"]
        pressure    = s["atmospheric pressure"]
        M1_interp = self.get_interpolated_coefficient(self.geolat,self.M,lat)
        
        s["S_mu"] = M1_interp * math.exp( (1013.25-pressure) /253.0)
        
    def setScalingFunctionMUfast(self, s):

        s["S_mu_fast"] = s["S_mu"]

    def get_interpolated_coefficient(self,geolat,a,lat):

        # We are interpolating from Lal's 10 degree latitude table
        # to a particular latitude

        # First make southern hemisphere latitudes positive (symmetry)
        lat = abs(lat)

        # Find vector indicies to interpolate between
        # Standard interpolation routine of Ken's

        A    = None
        B    = None
        i    = 0
        while i < (len(geolat) - 1):
            A = geolat[i]
            B = geolat[i+1]

            if ((A <= lat) and (lat <= B)):
                break;

            i = i + 1

        A_lat = A
        B_lat = B

        A_a = a[i]
        B_a = a[i+1]

        a_diff = B_a - A_a
        lat_diff = B_lat - A_lat
        targ_diff = lat - A_lat

        div     = a_diff / lat_diff
        product = targ_diff * div

        return A_a + product

# vim: ts=4:sw=4:et
