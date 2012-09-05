from ACE.Framework.Component     import Component
from ACE.Util.LeastSquaresSolver import LeastSquaresSolver
from ACE.Util.GammaStats         import *

import math
import scipy as Sci
import scipy.linalg
from numpy import *
from pylab import *

class OutputNuclideCalibration(Component):
    
    def __init__(self, collections, workflow):
        super(OutputNuclideCalibration, self).__init__(collections, workflow)
        self.constants = collections.get("constants")
        self.LAMBDA_36 = self.constants["lambda_36"]
        self.samples   = []

    def __call__(self, samples):
        self.samples += samples
        if len(self.samples) == self.workflow.total_samples:
            return self.process_samples(self.samples)
        return tuple()

    def process_samples(self, samples):
        
        numSamples = len(samples)

        # Solving the Matrix equation LHS = psi RHS by least squares:
        # LHS is the observed nuclide inventory minus contributions from muon production
        # RHS is the modelled nuclude inventory due to spallation (and including low 
        # energy netrons in the case of 36Cl) divided by the HLSL production rate
        # psi is the HLSL production rate
        
        # initialize matrices
        LHS = []
        LHS_weighted = []
        for i in range(numSamples):
            LHS.append([0.0])
            LHS_weighted.append([0.0])
            
        # initialize arrays
        RHS = []
        RHS_weighted = []
        for i in range(numSamples):
            RHS.append(0.0)
            RHS_weighted.append(0.0)

        Inv_err = []
        Inv_calc_err = []
        Inv_meas_err = []
        for i in range(numSamples):
            Inv_err.append(0.0)
            Inv_calc_err.append(0.0)
            Inv_meas_err.append(0.0)
        
        i = 0
        
        for s in self.samples:
            Inv_c           = s["cosmogenic inventory"]
            indAge          = s["independent age"]
            indAgeUnc       = s["independent age uncertainty"]
            InvcUncertainty = s["cosmogenic inventory uncertainty"]
         
            expterm         = math.exp(-self.LAMBDA_36 * indAge)
            expterm2        = expterm / (1.0 - expterm)
            Inv_calc_err[i]    = Inv_c * indAgeUnc * self.LAMBDA_36 * expterm2
            #Inv_calc_err    = Inv_c * indAgeUnc / indAge
            Inv_meas_err[i]    = InvcUncertainty 

            Inv_calc_err_2  = Inv_calc_err[i]**2.0
            Inv_meas_err_2  = Inv_meas_err[i]**2.0
            
            recip_sum = 1.0 / ( Inv_calc_err_2 + Inv_meas_err_2)
            
            Inv_err[i] = recip_sum**0.5
            
            LHS[i][0] = s["psi_spallation_coeff"]
            RHS[i]    = s["RHS_1"]
            
            LHS_weighted[i][0] = Inv_err[i] * LHS[i][0];
            RHS_weighted[i]    = Inv_err[i] * RHS[i];
            
            # s_id      = s["id"]
            #print LHS[i][0], RHS[i]
            #print LHS_weighted[i][0], RHS_weighted[i]

            #print s_id, LHS_weighted[i][0], LHS_weighted[i][1], LHS_weighted[i][2], RHS_weighted[i]
            #print s_id, Inv_err, Inv_meas_err, Inv_calc_err
            #print s_id, LHS[i][0], LHS[i][1], LHS[i][2], RHS[i]
            
            i = i + 1;

        # We now have LHS and RHS above, with each weighted by the 
        # experimental error (lab for observed, time for modelled)
        # Now estimate psi, the HLSL production rate
        # Use qr decomposition here
        numData = i          # Number of database samples
        numParams = 1        # Only considering spallation for non-36Cl
        (Q,R) = Sci.linalg.qr(LHS_weighted)
        R = R[0:numParams,:];
        Q = Q[:,0:numParams];
        psi_spallation_nuclide = dot(transpose(Q),RHS_weighted) / R

        # Calculate reduced chi-square
        nu = float(max(0, numData-numParams))
        yhat = LHS_weighted * psi_spallation_nuclide # Modelled Inventory
        r = RHS_weighted - transpose(yhat) # Residual between obs and modelled
        chisquare = 1/nu * dot(r,transpose(r))

        # Calculate 1-Sigma production rate uncertainty from Menke (1989)
        # Find inverse of covariance matrix
        deltaChi = 1.0 # 1-Sigma, 68.3%, 1 dof
        covMat = 1/nu * dot(transpose(LHS_weighted),LHS_weighted)
        invCovMat = Sci.linalg.solve(covMat,eye(numParams))
        psi_spallation_nuclide_one_sigma = sqrt(deltaChi) * sqrt(invCovMat)

        #Calculate probability of this fit not being random
        prob = (1.0 - gammq(nu / 2.0, (chisquare * i) / 2.0))*100

        #Plot results graphically (if selected)
        graphicsWanted = "true"
        #graphicsWanted = "false"

        if graphicsWanted == "true":
        # Make some vectors
           j = 0
           yhatList = []
           for i in range(numSamples):
              yhatList.append(0.0)

           while j <= i:
              yhatList[j] = float(psi_spallation_nuclide * LHS[j][0])
              j += 1 

           #Plot up
           ax = subplot(111)
           plot(RHS,yhatList,'o')
           sortedRHS = sort(RHS, 0, 'mergesort')
           plot(sortedRHS,sortedRHS) # Plot y = x  
           errorbar(RHS,yhatList,Inv_calc_err,Inv_meas_err,fmt='b.', ecolor=None)
           nuclide = self.experiment["nuclide"]
           experiment = self.experiment["name"]
           textlabel = "Calibration Results for Experiment: " + str(experiment)
           title(textlabel)
           xlabel('Observed Inventory - Muon Contribution')
           ylabel('Modelled Inventory (No Muon Contribution)')
           textlabel = "Production rate = %3.2f +- %3.2f  atoms / g / yr" % (float(psi_spallation_nuclide), float(psi_spallation_nuclide_one_sigma))
           text(0.05, 0.90,textlabel,transform = ax.transAxes,size = 14)
           textlabel = "Reduced Chi-Square = %3.2f" % float(chisquare)
           text(0.05, 0.85,textlabel,transform = ax.transAxes,size = 14)
           grid()
           show()
           #End of graphics section

        self.experiment["psi_spallation_nuclide"]     = float(psi_spallation_nuclide)
        self.experiment["psi_spallation_uncertainty"] = float(psi_spallation_nuclide_one_sigma)
        self.experiment["chi_square"]                 = float(chisquare)
        self.experiment["sample_size"]                = i
        self.experiment["probability"]                = float(prob)
        
        s = self.samples[0]
       
        self.experiment["post_calibrated_slowMuon"] = float(s["Pmu_slow"]/(psi_spallation_nuclide + s["Pmu_slow"] + s["Pmu_fast"]) * 100)
        self.experiment["post_calibrated_fastMuon"] = float(s["Pmu_fast"]/(psi_spallation_nuclide + s["Pmu_slow"] + s["Pmu_fast"]) * 100)

        return (([None], []),)
