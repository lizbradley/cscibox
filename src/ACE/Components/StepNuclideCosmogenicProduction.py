"""
StepNuclideCosmogenicProduction.py

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

import math

class StepNuclideCosmogenicProduction(Component):
    def __init__(self, collections, workflow):
        super(StepNuclideCosmogenicProduction, self).__init__(collections, workflow)
        self.constants = collections.get("Constants")

        self.LAMBDA_f  = self.constants["LAMBDA_f"]
        self.LAMBDA_mu = self.constants["LAMBDA_mu"]

    def init_sample(self, s):
        self.shielding_factor = s["shielding factor"]

    def __call__(self, samples):
        for s in samples:
            self.init_sample(s)

            self.calculateZs(s);
            self.calculateQ_s(s);
            self.calculateQ_mu(s);
            self.calculateP_sp_ca(s);
            self.calculateP_mu(s);
            self.calculateP_total(s);

        return (([self.get_connection()], samples),)

    def calculateZs(self, s):
        # calculate thickness * density
        s["Zs"] = s["thickness"] * s["density"]

    def calculateQ_s(self, s):
        # calculate (LAMBDA_f/Zs)*(1-EXP(-1*Zs/LAMBDA_f))
        div1  = self.LAMBDA_f / s["Zs"]
        div2  = -s["Zs"] / self.LAMBDA_f
        sub1  = 1.0 - math.exp(div2)
        s["Q_s"] = div1 * sub1

    def calculateQ_mu(self, s):
        # calculate LAMBDA_mu*(1-EXP(-Zs/LAMBDA_mu))/Zs
        div1 = -s["Zs"] / self.LAMBDA_mu
        sub  = 1.0 - math.exp(div1)
        s["Q_mu"] = (self.LAMBDA_mu * sub) / s["Zs"]

    def calculateP_sp_ca(self, s):
        pass

    def calculateP_mu(self, s):
        pass

    def calculateP_total(self, s):
        # calculate P_sp_ca+P_mu
        s["P_total"] = s["P_sp_ca"] + s["P_mu"]

# vim: ts=4:sw=4:et
