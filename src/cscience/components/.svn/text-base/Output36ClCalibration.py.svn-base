"""
Output36ClCalibration.py

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

from ACE.Framework.Component          import Component
from ACE.Util.LeastSquaresSolver import LeastSquaresSolver
from ACE.Util.GammaStats         import *

from ACE.GUI.Events.ProgressEvents import CalibrationPlotEvent
from ACE.GUI.Events.ProgressEvents import EVT_CALIBRATION_PLOT

import scipy as Sci
import scipy.linalg
from numpy import *
# from pylab import *

class Output36ClCalibration(Component):
    def __init__(self, collections, workflow):
        super(Output36ClCalibration, self).__init__(collections, workflow)
        self.constants = collections.get("Constants")
        self.LAMBDA_36 = self.constants["lambda_36"]
        self.samples = []

    def __call__(self, samples):
        self.samples += samples
        if len(self.samples) == self.workflow.total_samples:
            return self.process_samples()

        return tuple()

    def process_samples(self):
        numSamples = len(self.samples)

        # initialize matrices
        LHS = []
        LHS_weighted = []
        for i in range(numSamples):
            LHS.append([0.0, 0.0, 0.0])
            LHS_weighted.append([0.0, 0.0, 0.0])

        # initialize arrays
        RHS = []
        RHS_weighted = []
        for i in range(numSamples):
            RHS.append(0.0)
            RHS_weighted.append(0.0)

        Inv_err = []
        Inv_meas_err = []
        Inv_calc_err = []
        yhat = []
        yhat_weighted = []
        for i in range(numSamples):
            Inv_err.append(0.0)
            Inv_meas_err.append(0.0)
            Inv_calc_err.append(0.0)
            yhat.append(0.0)
            yhat_weighted.append(0.0)

        i = 0

        for s in self.samples:
            age       = s["age"]
            ageUnc    = s["age uncertainty"]
            Inv_c     = s["cosmogenic inventory"]
            indAge    = s["independent age"]
            indAgeUnc = s["independent age uncertainty"]
            P_total   = s["P_total"]
            InvmUncertainty = s["measured inventory uncertainty"]

            # Calculate weighting coefficients Inv_calc_err and Inv_meas_err
            expterm      = math.exp(-self.LAMBDA_36 * indAge)
            expterm2     = expterm / (1.0 - expterm)
            Inv_calc_err[i] = Inv_c * indAgeUnc * self.LAMBDA_36 * expterm2
            # Inv_calc_err = Inv_c * indAgeUnc / indAge

            Inv_meas_err[i]   = InvmUncertainty
            Inv_calc_err_2 = Inv_calc_err[i]**2.0
            Inv_meas_err_2 = Inv_meas_err[i]**2.0

            recip_sum = 1.0 / ( Inv_calc_err_2 + Inv_meas_err_2)

            Inv_err[i] = recip_sum**0.5

            LHS[i][0] = s["psi_ca_0_coeff"]
            LHS[i][1] = s["psi_k_0_coeff"]
            LHS[i][2] = s["Pf_0_coeff"]
            RHS[i]    = s["RHS_1"]

            LHS_weighted[i][0] = Inv_err[i] * LHS[i][0];
            LHS_weighted[i][1] = Inv_err[i] * LHS[i][1];
            LHS_weighted[i][2] = Inv_err[i] * LHS[i][2];
            RHS_weighted[i]    = Inv_err[i] * RHS[i];

            i = i + 1;

        norm_factor = 1e+24

        # We now have LHS and RHS above, with each weighted by the
        # experimental error (lab for observed, time for modelled)
        # Now estimate psi_ca_0, psu_k_0 and Pf_0, the HLSL 
        # production rates.  Use qr decomposition here
        numData = i # Number of samples in database
        numParams = 3 # Number of production mechanisms to constrain
        (Q,R) = Sci.linalg.qr(LHS_weighted)
        R = R[0:numParams,:];
        Q = Q[:,0:numParams];
        matmult = dot(transpose(Q),RHS_weighted)
        rates = Sci.linalg.solve(R,matmult)
        RI = Sci.linalg.solve(R,eye(numParams))

        psi_ca_0 = rates[0] / norm_factor
        psi_k_0  = rates[1] / norm_factor
        Pf_0     = rates[2]

        # Calculate reduced chi-square
        nu = float(max(0,numData - numParams))
        j = 0
        while j < i:
           yhat[j] = float(psi_ca_0) * norm_factor * LHS[j][0] + float(psi_k_0) * norm_factor * LHS[j][1] + float(Pf_0) * LHS[j][2] # Model Prediction
           yhat_weighted[j] = Inv_err[j] * yhat[j]
           j += 1

        r = RHS_weighted - transpose(yhat_weighted) # Residual between obs and mod
        normr = Sci.linalg.norm(r)
        chisquare = 1/nu * dot(r,transpose(r))

        # Calculate 1-Sigma production rate uncertainty from Menke (1989)
        deltaChi = 3.53 # 1-Sigma, prob 68.3%, 3 degrees of freedom
        covMat = 1/nu * dot(transpose(LHS_weighted),LHS_weighted)
        invCovMat = Sci.linalg.solve(covMat,eye(numParams)) #inverse covariance matrix
        psi_ca_0_one_sigma = sqrt(deltaChi)/(10 * norm_factor) * sqrt(invCovMat[0,0])
        psi_k_0_one_sigma = sqrt(deltaChi)/(10 * norm_factor) * sqrt(invCovMat[1,1])
        Pf_0_one_sigma = sqrt(deltaChi)/(10) * sqrt(invCovMat[2,2])

        #Calculate probability of this fit not being random
        prob = (1.0 - gammq(nu / 2.0, (chisquare * i) / 2.0))*100

        #Plot results graphically (if selected)
        graphicsWanted = "true"
        # graphicsWanted = "false"

        evt = CalibrationPlotEvent(data_rhs = RHS, data_yhat = yhat, data_calc_err = Inv_calc_err, data_meas_err = Inv_meas_err)
        wx.PostEvent(self.workflow.browser, evt)

        # if graphicsWanted == "true":
        #    ax=subplot(111)
        #    plot(RHS,yhat,'o')
        #    plot(sort(RHS,0,'mergesort'),sort(RHS,0,'mergesort')) # y = x
        #    errorbar(RHS,transpose(yhat),Inv_calc_err,Inv_meas_err,fmt='b.', ecolor=None)
        #    experiment = self.experiment["name"]
        #    title('Calibration Results for Experiment: ' + str(experiment))
        #    ylabel('Modelled Inventory (No Muon Contribution)')
        #    xlabel('Observed Inventory - Muon Contribution')
        #    textlabel = "Ca Production rate =  %3.2f +- %3.2f  atoms / g / yr" % (float(psi_ca_0 * 1.502E22) , float(psi_ca_0_one_sigma * 1.502E22))
        #    text(0.05, 0.90,textlabel,transform = ax.transAxes, size = 12)
        #    textlabel = "K  Production rate = %3.2f +- %3.2f  atoms / g / yr"  % (float(psi_k_0 * 1.54E22), float(psi_k_0_one_sigma * 1.54E22))
        #    text(0.05, 0.85,textlabel,transform = ax.transAxes, size = 12)
        #    textlabel = "N  Production rate = %3.2f +- %3.2f  atoms / g / yr" % (float(Pf_0), float(Pf_0_one_sigma))
        #    text(0.05, 0.80,textlabel,transform = ax.transAxes, size = 12)
        #    textlabel = "Reduced Chi-Square = %3.2f"  % float(chisquare)
        #    text(0.05, 0.75,textlabel,transform = ax.transAxes, size = 12)
        #    grid()
        #    show()
        self.experiment["psi_ca_0"]           = psi_ca_0
        self.experiment["psi_k_0"]            = psi_k_0
        self.experiment["Pf_0"]               = Pf_0
        self.experiment["psi_ca_uncertainty"] = psi_ca_0_one_sigma
        self.experiment["psi_k_uncertainty"]  = psi_k_0_one_sigma
        self.experiment["Pf_uncertainty"]     = Pf_0_one_sigma
        self.experiment["chi_square"]         = chisquare
        self.experiment["sample_size"]        = i
        self.experiment["probability"]        = prob

        return (([None], []),)

# vim: ts=4:sw=4:et
