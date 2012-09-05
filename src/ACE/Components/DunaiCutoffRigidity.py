"""
DunaiCutoffRigidity.py

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

Dunai doi : 10.1016/S0012-821X(99)00310-6
"""

from ACE.Framework.Component import Component
import math

class DunaiCutoffRigidity(Component):
    def __init__(self, collections, workflow):
        super(DunaiCutoffRigidity, self).__init__(collections, workflow)
        self.M0 = 8.084E+22		    # 1945 Dipole Moment
        self.mu_0 = 1.25663706E-6	# Permeability of Free Space
        self.c = 299792458		    # Speed of Light
        self.R = 6378.1E3		    # Radius of the Earth in m

    def __call__(self, samples):
        for s in samples:
            PI = math.pi

            #Calculate cutoff rigidity (Equation 2 of Dunai 2000, 2001)
            #Calculate Horizonal field component H
            M = self.M0 * s["paleomagnetic intensity"]
            cosLat = math.cos(s["paleomagnetic latitude"] * PI / 180.0)
            H = self.mu_0 * M * cosLat / (4.0 * PI * self.R**3.0)

            #Calculate tangent of Magnetic Inclination in radians
            tanInc = 2.0 * math.tan(s["paleomagnetic latitude"] * PI / 180.0)

            #Calculate cutoff rigidity
            num = self.R * H * self.c
            den = 4.0E9 * (1 + 0.25 * tanInc**2.0)**1.5
            s["rigidity"] = num / den

        return (([self.get_connection()], samples),)

# vim: ts=4:sw=4:et
