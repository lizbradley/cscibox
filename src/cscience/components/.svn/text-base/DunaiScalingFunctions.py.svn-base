"""
DunaiScalingFunctions.py

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

Dunai 2001 doi : 10.1016/S0012-821X(01)00503-9
Dunai 2000 doi : 10.1016/S0012-821X(99)00310-6
"""

from ACE.Framework.Component import Component
import math

class DunaiScalingFunctions(Component):
    def __init__(self, collections, workflow):
        super(DunaiScalingFunctions, self).__init__(collections, workflow)
        self.constants = collections.get("Constants")
        self.A_Dunai = 0.5221
        self.B_Dunai = -1.7211
        self.C_Dunai = 0.3345
        self.X_Dunai = 4.2822
        self.Y_Dunai = 0.4952
        self.a_Dunai = 17.183
        self.b_Dunai = 2.060
        self.c_Dunai = 5.9164
        self.x_Dunai = 2.2964
        self.y_Dunai = 130.11

    def __call__(self, samples):
        for s in samples:
            self.setScalingFunctionSP(s)
            self.setScalingFunctionTH(s)
            self.setScalingFunctionMU(s)
            self.setScalingFunctionMUfast(s)

        return (([self.get_connection()], samples),)

    def setScalingFunctionSP(self, s):
        # Calculate scaling from Dunai 2001.  See doi ref at the
        # header.  This is scaling for spallation, and also
        # calculates neutron scaling below (which is only relevant
        # for the case of 36Cl, which Dunai does not consider
        # The terms used below are as those defined in Dunai 2001

        # calculate N1030 (Equation 3 Dunai 2001)
        rigidity  = s["rigidity"]
        arg     = -1.0 * ( rigidity - self.X_Dunai ) / self.B_Dunai
        den     = ( 1 + math.exp(arg) )**self.C_Dunai
        N1030   = self.Y_Dunai + self.A_Dunai / den

        # calculate LAMBDA (Equation 4 Dunai 2001)
        arg     = -1.0 * ( rigidity - self.x_Dunai ) / self.b_Dunai
        den     = ( 1 + math.exp(arg) )**self.c_Dunai
        LAMBDA   = self.y_Dunai + self.a_Dunai / den

        # calculate z (Appendix of Dunai 2000)
        # find pressure difference between sea level and sample height
        # z is pressure difference * 10 / g_0

        g_0   = self.constants["g_0"]

        pressure = s["atmospheric pressure"]
        slpressure = s["sea level pressure"]

        pressurediff = slpressure - pressure
        z = pressurediff * 10.0 / g_0

        # calculate Scaling Factor (Equation 5 Dunai 2001)
        s["S_sp"] = N1030 * math.exp(z / LAMBDA)

    def setScalingFunctionTH(self, s):
        # No low energy scaling 
        s["S_th"]  = s["S_sp"]

    def setScalingFunctionMU(self, s):
        # Muons are the same as spallation but have a fixed attenuation length
        # (LAMBDA) of 247 g/cm2 (Appendix of Dunai 2000)
        # calculate N1030 (Equation 3)
        rigidity  = s["rigidity"]
        arg     = -1.0 * ( rigidity - self.X_Dunai ) / self.B_Dunai
        den     = ( 1 + math.exp(arg) )**self.C_Dunai
        N1030   = self.Y_Dunai + self.A_Dunai / den

        muon_att_coeff = 0.0
        muon_att_const = 247.0
        LAMBDA   = muon_att_coeff * rigidity + muon_att_const

        # calculate z (Appendix of Dunai 2000)
        # find pressure difference between sea level and sample height
        # z is pressure difference * 10 / g_0

        g_0   = self.constants["g_0"]

        pressure = s["atmospheric pressure"]
        slpressure = s["sea level pressure"]

        pressurediff = slpressure - pressure
        z = pressurediff * 10.0 / g_0

        # calculate Scaling Factor (Equation 5 of Dunai 2001)
        s["S_mu"] = N1030 * math.exp(z / LAMBDA)

    def setScalingFunctionMUfast(self, s):
        # No difference between fast and slow muons in Dunai scaling

        s["S_mu_fast"] = s["S_mu"]

# vim: ts=4:sw=4:et
