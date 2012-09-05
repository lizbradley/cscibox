"""
StepDiffusionEquation.py

Copyright (c) 2006-2007 University of Colorado. All rights reserved.
"""

from ACE.Framework.Component import Component

import math

class StepDiffusionEquation(Component):
    def __init__(self, collections, workflow):
        super(StepDiffusionEquation, self).__init__(collections, workflow)
        self.constants = collections.get("constants")
        self.elements = collections.get("elements")
        self.elemNames = ["O", "H", "C", "Na", "Mg", "Al", "Si", "P", "K", "Ca", "Ti", "Mn", "Fe", "Cl", "B", "Sm", "Gd", "U", "Th"]
        self.chemNames = ["CO2", "Na2O", "MgO", "Al2O3", "SiO2", "P2O5", "K2O", "CaO", "TiO2", "MnO", "Fe2O3", "Cl", "Cl uncertainty", "B", "Sm", "Gd", "U", "Th"]
        self.AV            = self.constants["AV"]
        self.A_a           = self.constants["A_a"]
        self.Da            = self.constants["Da"]
        self.D_eth_a       = self.constants["D_eth_a"]
        self.L_f_a         = self.constants["L_f_a"]
        self.La            = self.constants["La"]
        self.LAMBDA_f      = self.constants["LAMBDA_f"]
        self.P_eth_a       = self.constants["P_eth_a"]
        self.Phistar_eth_a = self.constants["phistar_eth_a"]
        self.S_eth_a       = self.constants["S_eth_a"]
        self.S_th_a        = self.constants["S_th_a"]
        self.SIGMA_eth_a   = self.constants["SIGMA_eth_a"]
        self.SIGMA_sc_a    = self.constants["SIGMA_sc_a"]

    def init_sample(self, s):
        self.chemistry = []
        for name in self.chemNames:
            self.chemistry.append(s[name])
        self.compositions = []
        for name in self.elemNames:
            self.compositions.append(s[name + "Calc"])

    def __call__(self, samples):

        for s in samples:
            # only perform calculations the first time through the loop
            if s["age"] == self.experiment["timestep"]:
                self.init_sample(s)

                self.calculateSIGMA_th_ss(s);
                self.calculateF_th(s);
                self.calculateIeff(s);
                self.calculateSIGMA_sc_ss(s);
                self.calculateB(s);
                self.calculateX_ss(s);
                self.calculateSIGMA_eth_ss(s);
                self.calculateA_ss(s);
                self.calculateR_eth(s);
                self.calculateD_eth_ss(s);
                self.calculatePhistar_eth_ss(s);
                self.calculateP_eth_ss(s);
                self.calculateR_th(s);
                self.calculatePhistar_th_ss(s);
                self.calculateF_eth(s);
                self.calculateL_th_ss(s);
                self.calculateDeltaPhistar_eth(s);
                self.calculateDeltaPhistar2_eth(s);
                self.calculateL_eth_ss(s);
                self.calculatePhistar_th_a(s);
                self.calculateL_eth_a(s);
                self.calculateDeltaPhistar_th(s);
                self.calculateFDeltaPhistar_eth_a(s);
                self.calculateFScrDeltaPhistar_eth_a(s);
                self.calculateFDeltaPhistar_eth(s);
                self.calculateFScrDeltaPhistar_eth_ss(s);
                self.calculateDeltaFDeltaPhistar_eth(s);
                self.calculateFScrDeltaPhistar_th_ss(s);

        return (([self.get_connection()], samples),)

    def calculateSIGMA_th_ss(self, s):
        total = 0.0
        for i in range(len(self.elemNames)):
            comp    = self.compositions[i]
            sigmaTH = self.elements[self.elemNames[i]]["sigmaTH"]
            total += comp * sigmaTH
        s["SIGMA_th_ss"] = total
        s["LAMBDA_th_ss"] = 1.0 / total

    def calculateF_th(self, s):
        ClCalc    = self.compositions[self.elemNames.index("Cl")];
        sigmaTH   = self.elements["Cl"]["sigmaTH"]
        s["f_th"] = sigmaTH * ClCalc / s["SIGMA_th_ss"]

    def calculateIeff(self, s):
        total = 0.0
        for i in range(len(self.elemNames)):
            comp  = self.compositions[i]
            iotaA = self.elements[self.elemNames[i]]["iotaA"]
            total += comp * iotaA
        s["Ieff"] = total

    def calculateSIGMA_sc_ss(self, s):
        total = 0.0
        for i in range(len(self.elemNames)):
            comp    = self.compositions[i]
            sigmaSC = self.elements[self.elemNames[i]]["sigmaSC"]
            total += comp * sigmaSC
        s["SIGMA_sc_ss"] = total

    def calculateB(self, s):
        total = 0.0
        for i in range(len(self.elemNames)):
            comp    = self.compositions[i]
            sigmaSC = self.elements[self.elemNames[i]]["sigmaSC"]
            xi      = self.elements[self.elemNames[i]]["xi"]
            total += comp * sigmaSC * xi
        s["B_diffusion"] = total

    def calculateX_ss(self, s):
        s["X_ss"] = s["B_diffusion"] / s["SIGMA_sc_ss"]

    def calculateSIGMA_eth_ss(self, s):
        s["SIGMA_eth_ss"]  = s["X_ss"] * (s["Ieff"] + s["SIGMA_sc_ss"])
        s["LAMBDA_eth_ss"] = 1.0 / s["SIGMA_eth_ss"]

    def calculateA_ss(self, s):
        total = 0.0
        for i in range(len(self.elemNames)):
            total += self.compositions[i]
        s["A_ss"] = self.AV / total

    def calculateR_eth(self, s):
        s["R_eth"] = (s["A_ss"] / self.A_a)**0.5

    def calculateD_eth_ss(self, s):
        # calculate 1/(3*SIGMA_sc_ss*(1-2/(3*A_ss)))
        s["D_eth_ss"] = 1.0 / (3.0 * s["SIGMA_sc_ss"] * (1.0 - (2.0 / (s["A_ss"] * 3.0))))
        s["D_th_ss"]  = s["D_eth_ss"]

    def calculatePhistar_eth_ss(self, s):
        # calculate Pf_0*R_eth/(SIGMA_eth_ss-D_eth_ss/LAMBDA_f^2)
        
        if not hasattr(self, "Pf_0"):
            try:
                self.Pf_0 = self.experiment["Pf_0"]
            except KeyError:
                self.Pf_0 = 1.0

        s["Phistar_eth_ss"] = self.Pf_0 * (s["R_eth"] / ( s["SIGMA_eth_ss"] - (s["D_eth_ss"] / (self.LAMBDA_f**2.0))))

    def calculateP_eth_ss(self, s):
        # calculate EXP(-Ieff/B)
        s["P_eth_ss"] = math.exp(-s["Ieff"]/s["B_diffusion"])

    def calculateR_th(self, s):
        # calculate P_eth_ss/P_eth_a
        s["R_th"] = s["P_eth_ss"] / self.P_eth_a

    def calculatePhistar_th_ss(self, s):
        # calculate P_eth_a*SIGMA_eth_ss*phistar_eth_ss*R_th/(SIGMA_th_ss-D_th_ss/LAMBDA_f^2)
        lf2 = self.LAMBDA_f**2.0
        div = s["D_th_ss"] / lf2
        sub = s["SIGMA_th_ss"] - div
        div = s["R_th"] / sub
        s["Phistar_th_ss"] = self.P_eth_a * s["SIGMA_eth_ss"] * s["Phistar_eth_ss"] * div

    def calculateF_eth(self, s):
        # calculate (Ia_cl*N_cl)/Ieff
        ClCalc = self.compositions[self.elemNames.index("Cl")];
        iotaA  = self.elements["Cl"]["iotaA"]
        s["f_eth"] = iotaA * ClCalc / s["Ieff"]

    def calculateL_th_ss(self, s):
        # calculate (D_th_ss/SIGMA_th_ss)^(1/2)
        s["L_th_ss"] = (s["D_th_ss"] / s["SIGMA_th_ss"])**0.5

    def calculateDeltaPhistar_eth(self, s):
        # calculate phistar_eth_a-phistar_eth_ss
        s["DeltaPhistar_eth"] = self.Phistar_eth_a - s["Phistar_eth_ss"]

    def calculateDeltaPhistar2_eth(self, s):
        # calculate phistar_eth_ss-D_eth_a*phistar_eth_a/D_eth_ss
        prod = self.D_eth_a * self.Phistar_eth_a
        div  = prod / s["D_eth_ss"]
        s["DeltaPhistar2_eth"] = s["Phistar_eth_ss"] - div

    def calculateL_eth_ss(self, s):
        # calculate ((1/(3*SIGMA_sc_ss))/(SIGMA_eth_ss))^0.5
        prod = 3.0 * s["SIGMA_sc_ss"]
        div  = 1.0 / prod
        div  = div / s["SIGMA_eth_ss"]
        s["L_eth_ss"] = div**0.5

    def calculatePhistar_th_a(self, s):
        # calculate P_eth_a*S_eth_a*phistar_eth_a/(S_th_a-Da/L_f_a^2)
        lfa2 = self.L_f_a**2.0
        div  = self.Da / lfa2
        sub  = self.S_th_a - div
        prod = self.P_eth_a * self.S_eth_a * self.Phistar_eth_a
        s["Phistar_th_a"] = prod / sub

    def calculateL_eth_a(self, s):
        # calculate 1/(3*SIGMA_sc_a*SIGMA_eth_a)^0.5
        s["L_eth_a"]  = 1.0 / ((3.0 * self.SIGMA_sc_a * self.SIGMA_eth_a)**0.5)

    def calculateDeltaPhistar_th(self, s):
        # calculate phistar_th_a-phistar_th_ss
        s["DeltaPhistar_th"] = s["Phistar_th_a"] - s["Phistar_th_ss"]

    def calculateFDeltaPhistar_eth_a(self, s):
        # calculate (D_eth_ss*(-DELTAphistar_eth/L_eth_ss)-
        #            D_eth_ss*DELTAphistar2_eth/L_f_a)/
        #           (D_eth_a/L_eth_a+D_eth_ss/L_eth_ss)

        div1  = -s["DeltaPhistar_eth"] / s["L_eth_ss"]
        prod1 = s["D_eth_ss"] * div1
        prod2 = s["D_eth_ss"] * s["DeltaPhistar2_eth"]
        div2  = prod2 / self.L_f_a
        sub1  = prod1 - div2
        div3  = self.D_eth_a / s["L_eth_a"]
        div4  = s["D_eth_ss"] / s["L_eth_ss"]
        sum1  = div3 + div4
        s["FDeltaPhistar_eth_a"] = sub1 / sum1

    def calculateFScrDeltaPhistar_eth_a(self, s):
        # calculate P_eth_a*SIGMA_eth_a*FDELTAphistar_eth_a/(S_th_a-Da/L_eth_a^2)

        lea2 = s["L_eth_a"]**2.0
        div  = self.Da / lea2
        sub  = self.S_th_a - div
        prod = self.P_eth_a * self.SIGMA_eth_a * s["FDeltaPhistar_eth_a"]
        s["FScrDeltaPhistar_eth_a"] = prod / sub

    def calculateFDeltaPhistar_eth(self, s):
        # calculate (D_eth_a*DELTAphistar_eth/L_eth_a-
        #            D_eth_ss*DELTAphistar2_eth/L_f_a)/
        #           (D_eth_a/L_eth_a+D_eth_ss/L_eth_ss)

        prod1 = self.D_eth_a * s["DeltaPhistar_eth"]
        prod2 = s["D_eth_ss"] * s["DeltaPhistar2_eth"]

        div1  = prod1 / s["L_eth_a"]
        div2  = prod2 / self.L_f_a

        sub1  = div1 - div2

        div3  = self.D_eth_a / s["L_eth_a"]
        div4  = s["D_eth_ss"] / s["L_eth_ss"]

        sum1  = div3 + div4

        s["FDeltaPhistar_eth"] = sub1 / sum1

    def calculateFScrDeltaPhistar_eth_ss(self, s):
        # calculate SIGMA_eth_ss*P_eth_a*FDELTAphistar_eth*R_th/(SIGMA_th_ss-D_th_ss/L_eth_ss^2)

        les2 = s["L_eth_ss"]**2.0

        div1 = s["D_th_ss"] / les2

        sub = s["SIGMA_th_ss"] - div1

        prod = s["SIGMA_eth_ss"] * self.P_eth_a * s["FDeltaPhistar_eth"] * s["R_th"]

        s["FScrDeltaPhistar_eth_ss"] = prod / sub

    def calculateDeltaFDeltaPhistar_eth(self, s):
        # calculate FscrDELTAphistar_eth_a-FscrDELTAphistar_eth_ss
        s["DeltaFDeltaPhistar_eth"] = s["FScrDeltaPhistar_eth_a"] - s["FScrDeltaPhistar_eth_ss"]

    def calculateFScrDeltaPhistar_th_ss(self, s):
        # calculate (Da*(phistar_th_a/L_f_a-FscrDELTAphistar_eth_a/L_eth_a)-
        #            D_th_ss*(phistar_th_ss/LAMBDA_th_ss+FscrDELTAphistar_eth_ss/L_eth_ss)+
        #            (Da/La)*(DELTAphistar_th+DELTAFDELTAphistar_eth))/
        #            (D_th_ss/L_th_ss+Da/La)

        sum1  = s["DeltaPhistar_th"] + s["DeltaFDeltaPhistar_eth"]
        div1  = self.Da / self.La
        prod1 = div1 * sum1

        div2  = s["Phistar_th_ss"] / s["LAMBDA_th_ss"]
        div3  = s["FScrDeltaPhistar_eth_ss"] / s["L_eth_ss"]
        sum2  = div2 + div3
        prod2 = s["D_th_ss"]  * sum2

        div4  = s["Phistar_th_a"] / self.L_f_a
        div5  = s["FScrDeltaPhistar_eth_a"] / s["L_eth_a"]
        sub1  = div4 - div5
        prod3 = self.Da * sub1

        term  = prod3 - prod2 + prod1

        div6  = s["D_th_ss"] / s["L_th_ss"]
        sum3  = div6 + div1

        s["FScrDeltaPhistar_th_ss"] = term / sum3

# vim: ts=4:sw=4:et
