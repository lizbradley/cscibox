from ACE.Framework.Component                        import Component
from ACE.Components.StepNuclideCosmogenicProduction import StepNuclideCosmogenicProduction

class SNCPDating(StepNuclideCosmogenicProduction):
    
    def __init__(self, collections, workflow):
        super(SNCPDating, self).__init__(collections, workflow)

    def calculateP_sp_ca(self, s):
        # calculate S_sp*shielding_factor*Q_s*(psi_sp_ca*N_ca)
        s["P_sp_ca"] = s["S_sp"] * self.shielding_factor * s["Q_s"] * self.experiment['psi_spallation_nuclide']
        
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

    def calculateP_total(self, s):
        super(SNCPDating, self).calculateP_total(s)
        
        s["P_total_uncertainty"] = s["P_sp_ca"] * self.experiment['psi_spallation_uncertainty']/self.experiment['psi_spallation_nuclide']
