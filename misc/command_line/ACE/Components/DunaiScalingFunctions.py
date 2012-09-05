"""
DunaiScalingFunctions.py

Copyright (c) 2006-2007 University of Colorado. All rights reserved.

Dunai 2001 doi : 10.1016/S0012-821X(01)00503-9
Dunai 2000 doi : 10.1016/S0012-821X(99)00310-6
"""

from ACE.Framework.Component import Component
import math

class DunaiScalingFunctions(Component):
    def __init__(self, collections, workflow):
        super(DunaiScalingFunctions, self).__init__(collections, workflow)
        self.constants = collections.get("constants")
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
