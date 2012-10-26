"""
OutputNuclideCalibration.py

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

import wx

from ACE.Framework.Component     import Component
from ACE.Util.LeastSquaresSolver import LeastSquaresSolver
from ACE.Util.GammaStats         import *

from ACE.GUI.Events.ProgressEvents import CalibrationPlotEvent
from ACE.GUI.Events.ProgressEvents import EVT_CALIBRATION_PLOT

import math
import scipy as Sci
import scipy.linalg
from numpy import *
# from pylab import *

class OutputNuclideCalibration(Component):
    
    def __init__(self, collections, workflow):
        super(OutputNuclideCalibration, self).__init__(collections, workflow)
        self.constants = collections.get("Constants")
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

        evt = CalibrationPlotEvent(data_rhs = RHS, data_lhs = LHS, data_yhat = yhat, data_calc_err = Inv_calc_err, data_meas_err = Inv_meas_err)
        wx.PostEvent(self.workflow.browser, evt)

        self.experiment["psi_spallation_nuclide"]     = float(psi_spallation_nuclide)
        self.experiment["psi_spallation_uncertainty"] = float(psi_spallation_nuclide_one_sigma)
        self.experiment["chi_square"]                 = float(chisquare)
        self.experiment["sample_size"]                = i
        self.experiment["probability"]                = float(prob)
        
        s = self.samples[0]
       
        self.experiment["post_calibrated_slowMuon"] = float(s["Pmu_slow"]/(psi_spallation_nuclide + s["Pmu_slow"] + s["Pmu_fast"]) * 100)
        self.experiment["post_calibrated_fastMuon"] = float(s["Pmu_fast"]/(psi_spallation_nuclide + s["Pmu_slow"] + s["Pmu_fast"]) * 100)

        return (([None], []),)
