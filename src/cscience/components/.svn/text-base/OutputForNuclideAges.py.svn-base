"""
OutputForNuclideAges.py

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
from ACE.Framework.Nuclide    import Nuclide

import math

class OutputForNuclideAges(Component):
    
    def __call__(self, samples):

        self.timestep = self.experiment["timestep"]

        for s in samples:
            self.rewindAge(s);
            self.calculateInv_m(s);
            self.calculateInvmUncertainty(s);
            self.calculateAgeUncertainty(s);
            self.calculateAgeTotalUncertainty(s);
            self.calculatePinv(s);
            self.calculatePmean(s);

        return (([self.get_connection()], samples),)

    def rewindAge(self, s):
        s["age"] = s["age"] - self.timestep

    def calculateInv_m(self, s):
        s["measured inventory"] = s["cosmogenic inventory"]

    def calculateInvmUncertainty(self, s):
        s["measured inventory uncertainty"] = s["cosmogenic inventory uncertainty"]

    def calculateAgeUncertainty(self, s):
        # calculate age*measured inventory uncertainty/Inv_c
        s["age uncertainty"] = (s["age"] * s["cosmogenic inventory uncertainty"]) / s["cosmogenic inventory"]
        # round to nearest timestep
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
        #Stable isotopes have no exponential decreasing effect
        if Nuclide.stable(self.experiment['nuclide']):
            num = s["cosmogenic inventory"]
            denom = s["age"]
        s["production rate invariant"] = num/denom

    def calculatePmean(self, s):
        #So far s["production rate total"] is sum of production rates with time
        #we want the mean production rate with time ie / number of timesteps
        if s["production rate total"] > 0:
          s["production rate total"] = s["production rate total"] * self.timestep / (s["age"] - 0 * self.timestep)
          s["production rate spallation"] = s["production rate spallation"] * self.timestep / (s["age"] - 0 * self.timestep)
          s["scaling spallation"] = s["scaling spallation"] * self.timestep / (s["age"] - 0 * self.timestep)
          s["production rate low-energy"] = s["production rate low-energy"] * self.timestep / (s["age"] - 0 * self.timestep)
          s["scaling low-energy"] = s["scaling low-energy"] * self.timestep / (s["age"] - 0 * self.timestep)
          s["production rate muons"] = s["production rate muons"] * self.timestep / (s["age"] - 0 * self.timestep)
          s["scaling fast muons"] = s["scaling fast muons"] * self.timestep / (s["age"] - 0 * self.timestep)
          s["scaling slow muons"] = s["scaling slow muons"] * self.timestep / (s["age"] - 0 * self.timestep)


# vim: ts=4:sw=4:et
