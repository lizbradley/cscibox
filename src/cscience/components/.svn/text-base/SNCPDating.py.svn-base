"""
SNCPDating.py

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

from ACE.Framework.Component                        import Component
from ACE.Components.StepNuclideCosmogenicProduction import StepNuclideCosmogenicProduction
import math

class SNCPDating(StepNuclideCosmogenicProduction):
    
    def __init__(self, collections, workflow):
        super(SNCPDating, self).__init__(collections, workflow)

        self.constants = collections.get("Constants")

        self.LAMBDA_f    = self.constants["LAMBDA_f"]
        self.LAMBDA_mu   = self.constants["LAMBDA_mu"]

    def calculateP_sp_ca(self, s):
        # calculate S_sp*shielding_factor*Q_s*(psi_sp_ca*N_ca)
        s["P_sp_ca"] = s["S_sp"] * self.shielding_factor * s["Q_s"] * self.experiment['psi_spallation_nuclide']

        # check for erosion or burial
        if s["erosion rate"] or s["depth"] > 0:
           depthNow = s["density"] * (s["erosion rate"] * s["age"] + s["depth"])
           s["P_sp_ca"] = s["P_sp_ca"] * math.exp(-depthNow / self.LAMBDA_f)
        
    def calculateP_mu(self, s):
        # calculate S_mu*shielding_factor*Q_mu*Pmu_0

        #Turn percentage contributions from fast and slow muons into absolutes
        post_calibrated_slowMuon = self.experiment['post_calibrated_slowMuon']
        post_calibrated_fastMuon = self.experiment['post_calibrated_fastMuon']
        psi_spallation_nuclide = self.experiment['psi_spallation_nuclide']

        muonFrac = (post_calibrated_slowMuon + post_calibrated_fastMuon) / 100 
        s["Pmu_0"] = psi_spallation_nuclide / (1 - muonFrac) - psi_spallation_nuclide
        if muonFrac > 0:  # ie have a muogenic contribution
           s["Pmu_slow"] = post_calibrated_slowMuon / (100 * muonFrac) * s["Pmu_0"]
           s["Pmu_fast"] = post_calibrated_fastMuon / (100 * muonFrac) * s["Pmu_0"]
           s["P_mu"] = ( s["S_mu"] * s["Pmu_slow"] +  s["S_mu_fast"] * s["Pmu_fast"] ) * self.shielding_factor * s["Q_mu"]
        else:
           s["P_mu"] = 0.0

        # check for erosion or burial
        if s["erosion rate"] or s["depth"] > 0:
           depthNow = s["density"] * (s["erosion rate"] * s["age"] + s["depth"])
           s["P_mu"] = s["P_mu"] * math.exp(-depthNow / self.LAMBDA_mu)

    def calculateP_total(self, s):
        super(SNCPDating, self).calculateP_total(s)

        s["P_total_uncertainty"] = s["P_sp_ca"] * self.experiment['psi_spallation_uncertainty']/self.experiment['psi_spallation_nuclide']

        if s["production rate total"] >= 0:
          s["production rate total"] = s["production rate total"] + s["P_sp_ca"] + s["P_mu"]
          s["production rate spallation"] = s["production rate spallation"] + s["P_sp_ca"] 
          s["scaling spallation"] = s["scaling spallation"] + s["S_sp"]
          s["production rate muons"] = s["production rate muons"] + s["P_mu"]
          s["scaling fast muons"] = s["scaling fast muons"] + s["S_mu_fast"]
          s["scaling slow muons"] = s["scaling slow muons"] + s["S_mu"]
        else:
          s["production rate total"] = 0.0
          s["production rate spallation"] = 0.0
          s["scaling spallation"] = 0.0
          s["production rate low-energy"] = 0.0
          s["scaling low-energy"] = 0.0
          s["production rate muons"] = 0.0
          s["scaling fast muons"] = 0.0
          s["scaling slow muons"] = 0.0

