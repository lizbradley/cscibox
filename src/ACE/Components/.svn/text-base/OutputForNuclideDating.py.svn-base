"""
OutputForNuclideDating.py

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

from ACE.Components.OutputForNuclideAges  import OutputForNuclideAges

import math

class OutputForNuclideDating(OutputForNuclideAges):
    
    def __init__(self, collections, workflow):
        super(OutputForNuclideDating, self).__init__(collections, workflow)

    def __call__(self, samples):

        self.timestep = self.experiment["timestep"]

        super(OutputForNuclideDating, self).__call__(samples)

        return (([None], []),)

    def calculateInvmUncertainty(self, s):
        super(OutputForNuclideDating, self).calculateInvmUncertainty(s)
        sum1 = s["cosmogenic inventory uncertainty"]**2.0 + s["Inv_c_uncertainty"]**2.0
        #Use analytical error, not production rate error
        #s["Inv_err"] = sum
        s["Inv_err"] = s["cosmogenic inventory uncertainty"]

    def calculateAgeUncertainty(self, s):
        # calculate age*measured inventory uncertainty/Inv_c
        s["age uncertainty"] = (s["age"] * s["Inv_err"]) / s["cosmogenic inventory"]
        # round to nearest timestep
        s["age uncertainty"] = round (s["age uncertainty"] / self.timestep) * self.timestep

# vim: ts=4:sw=4:et
