"""
OutputFor36ClAges.py

Copyright (c) 2006-2007 University of Colorado. All rights reserved.
"""

from ACE.Framework.Component import Component

import math

class OutputFor36ClAges(Component):
    
    def __call__(self, samples):

        self.timestep = self.experiment["timestep"]

        for s in samples:
            self.calculateInv_m(s);
            self.calculateInvmUncertainty(s);
            self.calculateInv_c(s);
            self.calculateInvcUncertainty(s);
            self.calculateAgeUncertainty(s);

        return (([self.get_connection()], samples),)

    def calculateInv_m(self, s):
        # calculate ClCalc*ClRatio*0.000000000000001
        s["measured inventory"] = s["ClCalc"] * s["clRatio"] * 0.000000000000001

    def calculateInvmUncertainty(self, s):
        # calculate
        # SQRT(
        # (ClRatio*0.000000000000001)^2*(ClCalc*Cl uncertainty/Cl)^2+
        # ClCalc^2*(ClRatio*0.000000000000001*clRatio uncertainty/ClRatio)^2+
        # 2*(ClCalc*Cl uncertainty/Cl)^2*(ClRatio*0.000000000000001*clRatio uncertainty/ClRatio)^2
        # )
        units = 0.000000000000001

        ratioUnits = s["clRatio"] * units
        prod1      = s["ClCalc"] * s["Cl uncertainty"]
        prod2      = ratioUnits * s["clRatio uncertainty"]

        # print s["id"] + "[clRatio]: " + str(s["clRatio"])

        div1 = prod1 / s["Cl"]
        div2 = prod2 / s["clRatio"]

        pow1 = ratioUnits**2.0
        pow2 = div1**2.0
        pow3 = s["ClCalc"]**2.0
        pow4 = div2**2.0

        term1 = pow1 * pow2
        term2 = pow3 * pow4
        term3 = 2.0 * pow2 * pow4

        sum = term1 + term2 + term3

        s["measured inventory uncertainty"] = math.sqrt(sum)

    def calculateInv_c(self, s):
        # calculate Inv_m - Inv_r
        s["cosmogenic inventory"] = s["measured inventory"] - s["nucleogenic inventory"]

    def calculateInvcUncertainty(self, s):
        # calculate =SQRT(measured inventory uncertainty^2+(0.2*Inv_r)^2)
        prod1 = 0.2 * s["nucleogenic inventory"]
        term1 = s["measured inventory uncertainty"]**2.0
        term2 = prod1**2.0
        sum1  = term1 + term2

        s["cosmogenic inventory uncertainty"] = math.sqrt(sum1)

    def calculateAgeUncertainty(self, s):
        # calculate age*cosmogenic inventory uncertainty/Inv_c
        s["age uncertainty"] = (s["age"] * s["cosmogenic inventory uncertainty"]) / s["cosmogenic inventory"]
        # roundoff to nearest timestep
        s["age uncertainty"] = round (s["age uncertainty"] / self.timestep) * self.timestep

# vim: ts=4:sw=4:et
