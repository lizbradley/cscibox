"""
StepCosmogenicProduction.py

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

class StepCosmogenicProduction(Component):
    def __init__(self, collections, workflow):
        super(StepCosmogenicProduction, self).__init__(collections, workflow)
        self.constants = collections.get("Constants")
        self.elemNames = ["O", "H", "C", "Na", "Mg", "Al", "Si", "P", "K", "Ca", "Ti", "Mn", "Fe", "Cl", "B", "Sm", "Gd", "U", "Th"]

        self.LAMBDA_f  = self.constants["LAMBDA_f"]
        self.LAMBDA_mu = self.constants["LAMBDA_mu"]
        self.Ystar_ca  = self.constants["Ystar_ca"]
        self.Ystar_k   = self.constants["Ystar_k"]
        self.P_eth_a   = self.constants["P_eth_a"]
        self.Ys        = self.constants["Ys"]
        self.Yf        = self.constants["Yf"]

    def init_sample(self, s):
        self.compositions = []
        for name in self.elemNames:
            self.compositions.append(s[name + "Calc"])
        self.shielding_factor        = s["shielding factor"]
        self.Phistar_eth_ss          = s["Phistar_eth_ss"]
        self.Phistar_th_ss           = s["Phistar_th_ss"]
        self.R_eth                   = s["R_eth"]
        self.R_th                    = s["R_th"]
        self.FDeltaPhistar_eth       = s["FDeltaPhistar_eth"]
        self.FScrDeltaPhistar_eth_ss = s["FScrDeltaPhistar_eth_ss"]
        self.FScrDeltaPhistar_th_ss  = s["FScrDeltaPhistar_th_ss"]
        self.L_eth_ss                = s["L_eth_ss"]
        self.L_th_ss                 = s["L_th_ss"]
        self.P_eth_ss                = s["P_eth_ss"]
        self.LAMBDA_eth_ss           = s["LAMBDA_eth_ss"]
        self.f_eth                   = s["f_eth"]
        self.LAMBDA_th_ss            = s["LAMBDA_th_ss"]
        self.f_th                    = s["f_th"]

    def __call__(self, samples):

        try:
            self.psi_ca_0 = self.experiment["psi_ca_0"]
        except KeyError:
            self.psi_ca_0 = 0.0

        try:
            self.psi_k_0 = self.experiment["psi_k_0"]
        except KeyError:
            self.psi_k_0 = 0.0

        try:
            self.psi_mu_0 = self.experiment["psi_mu_0"]
        except AttributeError:
            self.psi_mu_0 = 0.0

        try:
            self.Pf_0 = self.experiment["Pf_0"]
        except KeyError:
            self.Pf_0 = 1.0

        try:
            self.psi_ca_uncertainty = self.experiment["psi_ca_uncertainty"]
        except KeyError:
            self.psi_ca_uncertainty = 0.0

        try:
            self.psi_k_uncertainty = self.experiment["psi_k_uncertainty"]
        except KeyError:
            self.psi_k_uncertainty = 0.0

        try:
            self.Pf_uncertainty = self.experiment["Pf_uncertainty"]
        except KeyError:
            self.Pf_uncertainty = 0.0
        
        try:
            self.psi_mu_0           = self.experiment["psi_mu_0"]
        except KeyError:
            self.psi_mu_0 = 0.0

        try:
            self.phi_mu_f0          = self.experiment["phi_mu_f0"]
        except KeyError:
            self.phi_mu_f0 = 0.0

        for s in samples:
            self.init_sample(s)

            self.calculateP_mu_n_0(s);
            self.calculateR_mu(s);
            self.calculateR_mu_p(s);
            self.calculateZs(s);
            self.calculateQ_s(s);
            self.calculateQ_mu(s);
            self.calculateQ_th(s);
            self.calculateQ_eth(s);
            self.calculateP_sp_ca(s);
            self.calculateP_sp_k(s);
            self.calculatePmu_0(s);
            self.calculateP_mu(s);
            self.calculatePn(s);
            self.calculateP_total(s);

        return (([self.get_connection()], samples),)

    def calculateP_mu_n_0(self, s):
        # calculate Ys*Psi_mu_0+0.0000058*Yf*phi_mu_f0
        s["P_mu_n_0"] = self.Ys * self.psi_mu_0 + 5.8E-6 * self.Yf * self.phi_mu_f0

    def calculateR_mu(self, s):
        # calculate S_mu*P_mu_n_0/(S_sp*Pf_0*R_eth)
        s["R_mu"] = s["S_mu"] * (s["P_mu_n_0"] / (s["S_sp"] * self.Pf_0 * s["R_eth"]))

    def calculateR_mu_p(self, s):
        # calculate R_mu*P_eth_a/P_eth_ss
        s["R_mu_p"] = s["R_mu"] * (self.P_eth_a / s["P_eth_ss"])

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

    def calculateQ_th(self, s):
        # calculate the following unbeliveable equation!!
        # (phistar_th_ss*LAMBDA_f*(1-EXP(-Zs/LAMBDA_f))+
        # (1+R_mu_p)*FscrDELTAphistar_eth_ss*L_eth_ss*(1-EXP(-Zs/L_eth_ss))+
        # (1+R_mu_p*R_th)*FscrDELTAphistar_th_ss*L_th_ss*(1-EXP(-Zs/L_th_ss))+
        # R_mu_p*phistar_th_ss*LAMBDA_mu*(1-EXP(-Zs/LAMBDA_mu))
        # )
        #
        # /
        #
        # (Zs*
        # (phistar_th_ss+
        # (1+R_mu_p)*FscrDELTAphistar_eth_ss+
        # (1+R_mu_p*R_th)*FscrDELTAphistar_th_ss+
        # R_mu_p*phistar_th_ss
        # )
        # )

        sum1  = 1.0 + s["R_mu_p"]
        prod1 = s["R_mu_p"] * self.R_th
        sum2  = 1.0 + prod1
        prod2 = sum1 * self.FScrDeltaPhistar_eth_ss
        prod3 = sum2 * self.FScrDeltaPhistar_th_ss
        prod4 = s["R_mu_p"] * self.Phistar_th_ss
        sum3  = self.Phistar_th_ss + prod2 + prod3 + prod4

        denominator = s["Zs"] * sum3

        div1 = -s["Zs"] / self.LAMBDA_f
        div2 = -s["Zs"] / self.L_eth_ss
        div3 = -s["Zs"] / self.L_th_ss
        div4 = -s["Zs"] / self.LAMBDA_mu

        exp1 = math.exp(div1)
        exp2 = math.exp(div2)
        exp3 = math.exp(div3)
        exp4 = math.exp(div4)

        sub1 = 1.0 - exp1
        sub2 = 1.0 - exp2
        sub3 = 1.0 - exp3
        sub4 = 1.0 - exp4

        prod1 = self.Phistar_th_ss * self.LAMBDA_f * sub1
        prod2 = sum1 * self.FScrDeltaPhistar_eth_ss * self.L_eth_ss * sub2
        prod3 = sum2 * self.FScrDeltaPhistar_th_ss * self.L_th_ss * sub3
        prod4 = s["R_mu_p"] * self.Phistar_th_ss * self.LAMBDA_mu * sub4

        numerator = prod1 + prod2 + prod3 + prod4

        s["Q_th"] = numerator / denominator

    def calculateQ_eth(self, s):
        # calculate
        # (
        # phistar_eth_ss*LAMBDA_f*(1-EXP(-Zs/LAMBDA_f))+
        # (1+R_mu*R_eth)*FDELTAphistar_eth*L_eth_ss*(1-EXP(-Zs/L_eth_ss))+
        # R_mu*phistar_eth_ss*LAMBDA_mu*(1-EXP(-Zs/LAMBDA_mu))
        # )
        #
        # /
        #
        # (
        # Zs*
        # (phistar_eth_ss+(1+R_mu*R_eth)*FDELTAphistar_eth+
        # R_mu*phistar_eth_ss
        # )
        # )

        prod1 = s["R_mu"] * self.R_eth
        sum1  = 1.0 + prod1

        div1 = -s["Zs"] / self.LAMBDA_f
        div2 = -s["Zs"] / self.L_eth_ss
        div3 = -s["Zs"] / self.LAMBDA_mu

        exp1 = math.exp(div1)
        exp2 = math.exp(div2)
        exp3 = math.exp(div3)

        sub1 = 1.0 - exp1
        sub2 = 1.0 - exp2
        sub3 = 1.0 - exp3

        prod2 = self.Phistar_eth_ss * self.LAMBDA_f * sub1
        prod3 = sum1 * self.FDeltaPhistar_eth * self.L_eth_ss * sub2
        prod4 = s["R_mu"] * self.Phistar_eth_ss * self.LAMBDA_mu * sub3

        numerator = prod2 + prod3 + prod4

        prod1 = sum1 * self.FDeltaPhistar_eth
        prod2 = s["R_mu"] * self.Phistar_eth_ss

        sum2 = self.Phistar_eth_ss + prod1 + prod2

        denominator = s["Zs"] * sum2

        s["Q_eth"] = numerator / denominator

    def calculateP_sp_ca(self, s):
        # calculate S_sp*shielding_factor*Q_s*(psi_ca_0*N_ca)
        CaCalc = self.compositions[self.elemNames.index("Ca")];
        prod1  = self.psi_ca_0 * CaCalc
        s["P_sp_ca"] = s["S_sp"] * self.shielding_factor * s["Q_s"] * prod1

    def calculateP_sp_k(self, s):
        # calculate S_sp*shielding_factor*Q_s*(psi_k_0*N_k)
        KCalc  = self.compositions[self.elemNames.index("K")];
        prod1  = self.psi_k_0 * KCalc
        s["P_sp_k"] = s["S_sp"] * self.shielding_factor * s["Q_s"] * prod1

    def calculatePmu_0(self, s):
        # calculate (N_ca*Ystar_ca+N_k*Ystar_k)*psi_mu_0
        CaCalc = self.compositions[self.elemNames.index("Ca")];
        KCalc  = self.compositions[self.elemNames.index("K")];

        prod1 = CaCalc * self.Ystar_ca
        prod2 = KCalc  * self.Ystar_k
        sum   = prod1 + prod2

        s["Pmu_0"] = sum * self.psi_mu_0

    def calculateP_mu(self, s):
        # calculate S_mu*shielding_factor*Q_mu*Pmu_0
        s["P_mu"] = s["S_mu"] * self.shielding_factor * s["Q_mu"] * s["Pmu_0"]

    def calculatePn(self, s):
        # calculate
        # S_th*shielding_factor*Q_th*f_th/LAMBDA_th_ss*
        # (phistar_th_ss+(1+R_mu_p)*FScrDeltaPhistar_eth_ss+
        # (1+R_mu_p*R_th)*FScrDeltaPhistar_th_ss+
        # R_mu_p*Phistar_th_ss
        # )+
        # S_th*shielding_factor*Q_eth*(1-P_eth_ss)*f_eth/LAMBDA_eth_ss*
        # (Phistar_eth_ss+(1+R_mu*R_eth)*FDeltaPhistar_eth+
        # R_mu*Phistar_eth_ss)

        # calculate 1+R_mu*R_eth
        prod2 = s["R_mu"] * self.R_eth
        sum3  = 1.0 + prod2

        # calculate 1-P_eth_ss
        sub1 = 1.0 - self.P_eth_ss

        # calculate (1+R_mu*R_eth)*FDeltaPhistar_eth
        prod3 = sum3 * self.FDeltaPhistar_eth

        # calculate R_mu*Phistar_eth_ss
        prod4 = s["R_mu"] * self.Phistar_eth_ss
        sum4  = self.Phistar_eth_ss + prod3 + prod4

        # calculate f_eth/LAMBDA_eth_ss

        div1  = self.f_eth / self.LAMBDA_eth_ss
        term2 = s["S_th"] * self.shielding_factor * s["Q_eth"] * sub1 * div1 * sum4

        # calculate 1+R_mu_p*R_th
        prod1 = s["R_mu_p"] * self.R_th
        sum1  = 1.0 + prod1

        # calculate 1+R_mu_p
        sum2 = 1.0 + s["R_mu_p"]

        # calculate R_mu_p*Phistar_th_ss
        prod5 = s["R_mu_p"] * self.Phistar_th_ss

        # calculate (1+R_mu_p*R_th)*FScrDeltaPhistar_th_ss
        prod6 = sum1 * self.FScrDeltaPhistar_th_ss

        # calculate (1+R_mu_p)*FScrDeltaPhistar_eth_ss
        prod7 = sum2 * self.FScrDeltaPhistar_eth_ss

        sum5  = self.Phistar_th_ss + prod7 + prod6 + prod5

        div2 = self.f_th / self.LAMBDA_th_ss

        term1 = s["S_th"] * self.shielding_factor * s["Q_th"] * div2 * sum5

        s["Pn"] = term1 + term2

    def calculateP_total(self, s):
        # calculate P_sp_ca+P_sp+k+P_mu+Pn;
        s["P_total"] = s["P_sp_ca"] + s["P_sp_k"] + s["P_mu"] + s["Pn"]

# vim: ts=4:sw=4:et
