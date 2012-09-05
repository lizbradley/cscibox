"""
InventoryChangeCalculation.py

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

class InventoryChangeCalculation(Component):
    def __init__(self, collections, workflow):
        super(InventoryChangeCalculation, self).__init__(collections, workflow)
        self.constants = collections.get("Constants")
        self.LAMBDA_36 = self.constants["lambda_36"]
        

    def __call__(self, samples):
        for s in samples:
            if s["age"] == self.experiment["timestep"]:
                # first time step. Set the 'modelled' inventory Inv_c_mod
                s["Inv_c_mod"] = (s["ClCalc"] * s["clRatio"] * 0.000000000000001) - s["nucleogenic inventory"]
                s["Inv_c_uncertainty"] = 0.0
            else:
                self.calculate_age(s)

        return (([self.get_connection()], samples),)

    def calculate_age(self, s):
        # calculate how much the inventory has changed over the timestep
        # also wind the age back timestep (10) years
        prod0 = -1.0 * self.LAMBDA_36 * self.experiment["timestep"]
        minu1 = 1.0 - math.exp(prod0)
        term1 = minu1 / self.LAMBDA_36
        prod1 = s["P_total"] * term1
        #prod1 = s["P_total"] * self.experiment["timestep"]
        prod2 = -1.0 * self.LAMBDA_36 * s["age"]
        prod3 = math.exp(prod2)
        prod4 = prod3 * prod1
        s["Inv_c_mod"] -= prod4
        prod5 = s["P_total_uncertainty"] * term1
        #prod5 = s["P_total_uncertainty"] * self.experiment["timestep"]
        prod6 = prod3 * prod5
        s["Inv_c_uncertainty"] += prod6

# vim: ts=4:sw=4:et
