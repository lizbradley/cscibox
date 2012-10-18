"""
SNCPCalibration.py

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
from ACE.Framework.Nuclide                          import Nuclide
from ACE.Components.StepNuclideCosmogenicProduction import StepNuclideCosmogenicProduction

class SNCPCalibration(StepNuclideCosmogenicProduction):
    
    def __init__(self, collections, workflow):
        super(SNCPCalibration, self).__init__(collections, workflow)
        
    def calculateP_sp_ca(self, s):
        # calculate S_sp*shielding_factor*Q_s*(psi_sp_ca*N_ca)
        # nuclide    = self.experiment["nuclide"]
        #s["P_sp_ca"] = s["S_sp"] * self.shielding_factor * s["Q_s"] * Nuclide.psi_spallation_ca[nuclide]
        s["P_sp_ca"] = 0.0
        
    def calculateP_mu(self, s):
        # calculate contribution from fast and slow muons

        nuclide    = self.experiment["nuclide"]

        slowMuonPerc           = self.experiment["slowMuonPerc"]
        fastMuonPerc           = self.experiment["fastMuonPerc"]
        psi_spallation_nuclide = Nuclide.psi_spallation_total[nuclide]

        s["Pmu_slow"] = slowMuonPerc/(100) * psi_spallation_nuclide
        s["Pmu_fast"] = fastMuonPerc/(100) * psi_spallation_nuclide
        s["P_mu"] = (s["S_mu"] * s["Pmu_slow"] + s["S_mu_fast"] * s["Pmu_fast"]) * self.shielding_factor * s["Q_mu"]
