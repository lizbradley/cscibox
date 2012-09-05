
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
