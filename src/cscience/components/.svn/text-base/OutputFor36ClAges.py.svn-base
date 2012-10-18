"""
OutputFor36ClAges.py

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
"""

from ACE.Framework.Component import Component
from ACE.Framework.Nuclide   import Nuclide

import math

class OutputFor36ClAges(Component):
    
    def __call__(self, samples):

        self.timestep = self.experiment["timestep"]

        for s in samples:
            self.rewindAge(s);
            self.calculateInv_m(s);
            self.calculateInvmUncertainty(s);
            self.calculateInv_c(s);
            self.calculateInvcUncertainty(s);
            self.calculateAgeUncertainty(s);
            self.calculateAgeTotalUncertainty(s);
            self.calculatePinv(s);
            self.calculatePmean(s);

        return (([self.get_connection()], samples),)

    def rewindAge(self, s):
        s["age"] = s["age"] - self.timestep

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

    def calculateAgeTotalUncertainty(self, s):
        # calculate uncertainty including from production rate uncertainty
        if s["Inv_c_uncertainty"] > 0:
          sum1 = math.sqrt(s["cosmogenic inventory uncertainty"]**2.0 + s["Inv_c_uncertainty"]**2.0)
        else:
          sum1 = s["cosmogenic inventory uncertainty"]

        s["age uncertainty total"] = (s["age"] * sum1) / s["cosmogenic inventory"]
        # round to nearest timestep
        s["age uncertainty total"] = round (s["age uncertainty total"] / self.timestep) * self.timestep

    def calculatePinv(self, s):
        self.LAMBDA_36 = Nuclide.decay[self.experiment['nuclide']]
        # calculate time invariant production rate

        prod0 = -1.0 * self.LAMBDA_36 * s["age"]
        denom = 1.0 - math.exp(prod0)
        num = s["cosmogenic inventory"] * self.LAMBDA_36
        s["production rate invariant"] = num/denom

    def calculatePmean(self, s):
        #So far s["production rate total"] is sum of production rates with time
        #we want the mean production rate with time ie / number of timesteps 
        if s["production rate total"] > 0:
          s["production rate total"] = s["production rate total"] * self.timestep / s["age"]
          s["production rate spallation"] = s["production rate spallation"] * self.timestep / s["age"]
          s["scaling spallation"] = s["scaling spallation"] * self.timestep / s["age"]
          s["production rate low-energy"] = s["production rate low-energy"] * self.timestep / s["age"]
          s["scaling low-energy"] = s["scaling low-energy"] * self.timestep / s["age"]
          s["production rate muons"] = s["production rate muons"] * self.timestep / s["age"]
          s["scaling fast muons"] = s["scaling fast muons"] * self.timestep / s["age"]
          s["scaling slow muons"] = s["scaling slow muons"] * self.timestep / s["age"]

# vim: ts=4:sw=4:et
