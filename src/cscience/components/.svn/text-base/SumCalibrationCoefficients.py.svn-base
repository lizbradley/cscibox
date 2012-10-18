"""
SumCalibrationCoefficients.py

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

class SumCalibrationCoefficients(Component):
    def __init__(self, collections, workflow):
        super(SumCalibrationCoefficients, self).__init__(collections, workflow)
        self.constants = collections.get("Constants")

        self.Da          = self.constants["Da"]
        self.D_eth_a     = self.constants["D_eth_a"]
        self.La          = self.constants["La"]
        self.L_f_a       = self.constants["L_f_a"]
        self.LAMBDA_f    = self.constants["LAMBDA_f"]
        self.LAMBDA_mu   = self.constants["LAMBDA_mu"]
        self.LAMBDA_36   = self.constants["lambda_36"]
        self.P_eth_a     = self.constants["P_eth_a"]
        self.S_eth_a     = self.constants["S_eth_a"]
        self.S_th_a      = self.constants["S_th_a"]
        self.SIGMA_eth_a = self.constants["SIGMA_eth_a"]
        self.Ys          = self.constants["Ys"]
        self.Yf          = self.constants["Yf"]

    def init_sample(self, s):
        self.ClRatio          = s["clRatio"]
        self.CaCalc           = s["CaCalc"]
        self.ClCalc           = s["ClCalc"]
        self.Inv_r            = s["nucleogenic inventory"]
        self.age              = s["age"]
        self.independent_age  = s["independent age"]
        self.D_eth_ss         = s["D_eth_ss"]
        self.D_th_ss          = s["D_th_ss"]
        self.f_eth            = s["f_eth"]
        self.f_th             = s["f_th"]
        self.KCalc            = s["KCalc"]
        self.L_eth_a          = s["L_eth_a"]
        self.L_eth_ss         = s["L_eth_ss"]
        self.L_th_ss          = s["L_th_ss"]
        self.LAMBDA_eth_ss    = s["LAMBDA_eth_ss"]
        self.LAMBDA_th_ss     = s["LAMBDA_th_ss"]
        self.P_eth_ss         = s["P_eth_ss"]
        self.Pmu_0            = s["Pmu_0"]
        self.Q_mu             = s["Q_mu"]
        self.Q_s              = s["Q_s"]
        self.R_eth            = s["R_eth"]
        self.R_th             = s["R_th"]
        self.S_el             = s["S_sp"]
        self.S_mu             = s["S_mu"]
        self.S_th             = s["S_th"]
        self.SIGMA_eth_ss     = s["SIGMA_eth_ss"]
        self.SIGMA_th_ss      = s["SIGMA_th_ss"]
        self.shielding_factor = s["shielding factor"]
        self.Zs               = s["Zs"]

    def __call__(self, samples):

        try:
            self.phi_mu_f0 = self.experiment["phi_mu_f0"]
        except KeyError:
            self.phi_mu_f0 = 0.0

        for s in samples:
            self.init_sample(s)

            if s["age"] == self.experiment["timestep"]:
                self.calculateIntermediateTerms()
                self.calculateNeutronCalibTerms(s)
            self.calculateTimesteppingCoeffs(s)

        return (([self.get_connection()], samples),)

    def calculateIntermediateTerms(self):
        # calculate terms used in the expression for neutron calibration

        div1 = -(self.Zs) / self.L_eth_ss
        sub1 = 1.0 - math.exp(div1)
        self.first = self.D_eth_a * sub1

        self.second = 1.0 - self.P_eth_ss

        pow3 = self.LAMBDA_f**2.0
        div3 = self.D_eth_ss / pow3
        self.third = self.SIGMA_eth_ss - div3

        pow4 = self.L_eth_ss**2.0
        div4 = self.D_th_ss / pow4
        self.fourth = self.SIGMA_th_ss - div4

        div5 = -(self.Zs) / self.L_th_ss
        self.fifth = 1.0 - math.exp(div5)

        div6 = self.D_eth_a / pow3
        self.sixth = self.SIGMA_eth_a - div6

        div9 = -(self.Zs) / self.LAMBDA_f
        self.ninth = 1.0 - math.exp(div9)

        self.tenth = self.D_th_ss / pow3

        self.eleventh = self.D_th_ss / self.L_th_ss

        div13a = self.D_eth_a / self.L_eth_a
        div13b = self.D_eth_ss / self.L_eth_ss
        self.thirteenth = div13a + div13b

        self.fourteenth = self.L_th_ss * self.P_eth_a

        div15 = self.Da / (self.L_eth_a**2.0)
        self.fifteenth = self.S_th_a - div15

        self.sixteenth = self.eleventh + (self.Da / self.La)

        self.seventeenth = self.SIGMA_th_ss - self.tenth

        self.eighteenth = self.SIGMA_eth_ss - (self.D_eth_ss / pow3)

        self.nineteenth = sub1

        div20 = self.Da / self.L_f_a
        self.twentieth = self.S_th_a - (div20**2.0)

        self.twentyfirst = self.S_th_a - (self.Da / (self.L_f_a**2.0))

        self.twentysecond = 1 - math.exp( -(self.Zs) / self.LAMBDA_mu)

    def calculateNeutronCalibTerms(self, s):
        # Calculate neut_lin_term[i]=ST[i]/Zs[i]*
            # (first[i]*feth[i]*L_eth_ss[i]*second[i]/
                # (LAMBDA_eth_ss[i]*L_eth_a*thirteenth[i]*sixth[i])+
            # first[i]*feth[i]*L_eth_ss[i]*second[i]/
                # (LAMBDA_eth_ss[i]*thirteenth[i]*L_f_a*sixth[i])+
            # ninth[i]*feth[i]*LAMBDA_f*second[i]*R_eth[i]/
                # (LAMBDA_eth_ss[i]*third[i])-
            # first[i]*feth[i]*L_eth_ss[i]*second[i]*R_eth[i]/
                # (LAMBDA_eth_ss[i]*L_eth_a*thirteenth[i]*third[i])-
            # D_eth_ss[i]*nineteenth[i]*feth[i]*L_eth_ss[i]*second[i]*R_eth[i]/
                # (LAMBDA_eth_ss[i]*thirteenth[i]*L_f_a*third[i])+
            # ninth[i]*f_th[i]*LAMBDA_f*P_eth_a*R_eth[i]*R_th[i]*SIGMA_eth_ss[i]/
                # (LAMBDA_th_ss[i]*third[i]*seventeenth[i])-
            # D_th_ss[i]*fifth[i]*f_th[i]*fourteenth[i]*R_eth[i]*R_th[i]*SIGMA_eth_ss[i]/
                # (Math.pow(LAMBDA_th_ss[i],2)*sixteenth[i]*third[i]*seventeenth[i])-
            # Da*fifth[i]*f_th[i]*fourteenth[i]*R_eth[i]*R_th[i]*SIGMA_eth_ss[i]/
                # (La*LAMBDA_th_ss[i]*sixteenth[i]*eighteenth[i]*seventeenth[i])+
            # first[i]*f_th[i]*L_eth_ss[i]*P_eth_a*R_th[i]*SIGMA_eth_ss[i]/
                # (LAMBDA_th_ss[i]*L_eth_a*thirteenth[i]*sixth[i]*fourth[i])+
            # first[i]*f_th[i]*L_eth_ss[i]*P_eth_a*R_th[i]*SIGMA_eth_ss[i]/
                # (LAMBDA_th_ss[i]*thirteenth[i]*L_f_a*sixth[i]*fourth[i])-
            # Da*D_eth_a*fifth[i]*f_th[i]*fourteenth[i]*R_th[i]*SIGMA_eth_ss[i]/
                # (La*LAMBDA_th_ss[i]*L_eth_a*thirteenth[i]*sixteenth[i]*sixth[i]*fourth[i])-
            # D_eth_a*D_th_ss[i]*fifth[i]*f_th[i]*fourteenth[i]*R_th[i]*SIGMA_eth_ss[i]/
                # (LAMBDA_th_ss[i]*L_eth_a*thirteenth[i]*L_eth_ss[i]*sixteenth[i]*sixth[i]*fourth[i])-
            # Da*D_eth_a*fifth[i]*f_th[i]*L_th_ss[i]*P_eth_a*R_th[i]*SIGMA_eth_ss[i]/
                # (La*LAMBDA_th_ss[i]*thirteenth[i]*L_f_a*sixteenth[i]*sixth[i]*fourth[i])-
            # D_eth_a*D_th_ss[i]*fifth[i]*f_th[i]*fourteenth[i]*R_th[i]*SIGMA_eth_ss[i]/
                # (LAMBDA_th_ss[i]*thirteenth[i]*L_eth_ss[i]*L_f_a*sixteenth[i]*sixth[i]*fourth[i])-
            # first[i]*f_th[i]*L_eth_ss[i]*P_eth_a*R_eth[i]*R_th[i]*SIGMA_eth_ss[i]/
                # (LAMBDA_th_ss[i]*L_eth_a*thirteenth[i]*third[i]*fourth[i])-
            # D_eth_ss[i]*nineteenth[i]*f_th[i]*L_eth_ss[i]*P_eth_a*R_eth[i]*R_th[i]*SIGMA_eth_ss[i]/
                # (LAMBDA_th_ss[i]*thirteenth[i]*L_f_a*third[i]*fourth[i])+
            # Da*D_eth_a*fifth[i]*f_th[i]*fourteenth[i]*R_eth[i]*R_th[i]*SIGMA_eth_ss[i]/
                # (La*LAMBDA_th_ss[i]*L_eth_a*thirteenth[i]*sixteenth[i]*eighteenth[i]*fourth[i])+
            # D_eth_a*D_th_ss[i]*fifth[i]*f_th[i]*L_th_ss[i]*P_eth_a*R_eth[i]*R_th[i]*SIGMA_eth_ss[i]/
                # (LAMBDA_th_ss[i]*L_eth_a*thirteenth[i]*L_eth_ss[i]*sixteenth[i]*third[i]*fourth[i])+
            # Da*D_eth_ss[i]*fifth[i]*f_th[i]*fourteenth[i]*R_eth[i]*R_th[i]*SIGMA_eth_ss[i]/
                # (La*LAMBDA_th_ss[i]*thirteenth[i]*L_f_a*sixteenth[i]*third[i]*fourth[i])+
            # D_eth_ss[i]*D_th_ss[i]*fifth[i]*f_th[i]*fourteenth[i]*R_eth[i]*R_th[i]*SIGMA_eth_ss[i]/
                # (LAMBDA_th_ss[i]*thirteenth[i]*L_eth_ss[i]*L_f_a*sixteenth[i]*eighteenth[i]*fourth[i])-
            # Da*D_eth_ss[i]*fifth[i]*f_th[i]*L_th_ss[i]*P_eth_a*SIGMA_eth_a/
                # (La*LAMBDA_th_ss[i]*thirteenth[i]*L_eth_ss[i]*sixteenth[i]*sixth[i]*fifteenth[i])+
            # Da*D_eth_ss[i]*fifth[i]*f_th[i]*fourteenth[i]*SIGMA_eth_a/
                # (LAMBDA_th_ss[i]*L_eth_a*thirteenth[i]*L_eth_ss[i]*sixteenth[i]*sixth[i]*fifteenth[i])+
            # Da*D_eth_a*fifth[i]*f_th[i]*fourteenth[i]*SIGMA_eth_a/
                # (La*LAMBDA_th_ss[i]*thirteenth[i]*L_f_a*sixteenth[i]*sixth[i]*fifteenth[i])-
            # Da*D_eth_a*fifth[i]*f_th[i]*fourteenth[i]*SIGMA_eth_a/
                # (LAMBDA_th_ss[i]*L_eth_a*thirteenth[i]*L_f_a*sixteenth[i]*sixth[i]*fifteenth[i])+
            # Da*D_eth_ss[i]*fifth[i]*f_th[i]*fourteenth[i]*R_eth[i]*SIGMA_eth_a/
                # (La*LAMBDA_th_ss[i]*thirteenth[i]*L_eth_ss[i]*sixteenth[i]*third[i]*fifteenth[i])-
            # Da*D_eth_ss[i]*fifth[i]*f_th[i]*fourteenth[i]*R_eth[i]*SIGMA_eth_a/
                # (LAMBDA_th_ss[i]*L_eth_a*thirteenth[i]*L_eth_ss[i]*sixteenth[i]*third[i]*fifteenth[i])-
            # Da*D_eth_ss[i]*fifth[i]*f_th[i]*fourteenth[i]*R_eth[i]*SIGMA_eth_a/
                # (La*LAMBDA_th_ss[i]*thirteenth[i]*L_f_a*sixteenth[i]*third[i]*fifteenth[i])+
            # Da*D_eth_ss[i]*fifth[i]*f_th[i]*fourteenth[i]*R_eth[i]*SIGMA_eth_a/
                # (LAMBDA_th_ss[i]*L_eth_a*thirteenth[i]*L_f_a*sixteenth[i]*third[i]*fifteenth[i])+
            # Da*fifth[i]*f_th[i]*L_th_ss[i]*P_eth_a*S_eth_a/
                # (La*LAMBDA_th_ss[i]*sixteenth[i]*sixth[i]*twentieth[i])+
            # Da*fifth[i]*f_th[i]*fourteenth[i]*S_eth_a/
                # (LAMBDA_th_ss[i]*L_f_a*sixteenth[i]*sixth[i]*twentieth[i]))

        #Split this up into
            # num1 numerator of first term
            # den1 denominator of first term
            # div1 = num1/den1
            # total = ST/Zs*(div1 + div2 - div3 + ... + divn)

        # System.out.println(LAMBDA_eth_ss + " " + third);
        num1 = self.first * self.f_eth * self.L_eth_ss * self.second
        den1 = self.LAMBDA_eth_ss * self.L_eth_a * self.thirteenth * self.sixth
        div1 = num1 / den1

        num2 = self.first * self.f_eth * self.L_eth_ss * self.second
        den2 = self.LAMBDA_eth_ss * self.thirteenth * self.L_f_a * self.sixth
        div2 = num2 / den2

        num3 = self.ninth * self.f_eth * self.LAMBDA_f * self.second * self.R_eth
        den3 = self.LAMBDA_eth_ss * self.third;
        div3 = num3 / den3

        num4 = self.first * self.f_eth * self.L_eth_ss * self.second * self.R_eth
        den4 = self.LAMBDA_eth_ss * self.L_eth_a * self.thirteenth * self.third;
        div4 = num4 / den4

        num5 = self.D_eth_ss * self.nineteenth * self.f_eth * self.L_eth_ss * self.second * self.R_eth;
        den5 = self.LAMBDA_eth_ss * self.thirteenth * self.L_f_a * self.third;
        div5 = num5 / den5

        num6 = self.ninth * self.f_th * self.LAMBDA_f * self.P_eth_a * self.R_eth * self.R_th * self.SIGMA_eth_ss
        den6 = self.LAMBDA_th_ss * self.third * self.seventeenth
        div6 = num6 / den6

        num7 = self.D_th_ss * self.fifth * self.f_th * self.fourteenth * self.R_eth * self.R_th * self.SIGMA_eth_ss
        pow7 = self.LAMBDA_th_ss**2.0
        den7 = pow7 * self.sixteenth * self.third * self.seventeenth;
        div7 = num7 / den7

        num8 = self.Da * self.fifth * self.f_th * self.fourteenth * self.R_eth * self.R_th * self.SIGMA_eth_ss
        den8 = self.La * self.LAMBDA_th_ss * self.sixteenth * self.eighteenth * self.seventeenth
        div8 = num8 / den8

        num9 = self.first * self.f_th * self.L_eth_ss * self.P_eth_a * self.R_th * self.SIGMA_eth_ss;
        den9 = self.LAMBDA_th_ss * self.L_eth_a * self.thirteenth * self.sixth * self.fourth
        div9 = num9 / den9

        num10 = self.first * self.f_th * self.L_eth_ss * self.P_eth_a * self.R_th * self.SIGMA_eth_ss;
        den10 = self.LAMBDA_th_ss * self.thirteenth * self.L_f_a * self.sixth * self.fourth
        div10 = num10 / den10

        num11 = self.Da * self.D_eth_a * self.fifth * self.f_th * self.fourteenth * self.R_th * self.SIGMA_eth_ss
        den11 = self.La * self.LAMBDA_th_ss * self.L_eth_a * self.thirteenth * self.sixteenth * self.sixth * self.fourth
        div11 = num11 / den11

        num12 = self.D_eth_a * self.D_th_ss * self.fifth * self.f_th * self.fourteenth * self.R_th * self.SIGMA_eth_ss
        den12 = self.LAMBDA_th_ss * self.L_eth_a * self.thirteenth * self.L_eth_ss * self.sixteenth * self.sixth * self.fourth
        div12 = num12 / den12

        num13 = self.Da * self.D_eth_a * self.fifth * self.f_th * self.L_th_ss * self.P_eth_a * self.R_th * self.SIGMA_eth_ss;
        den13 = self.La * self.LAMBDA_th_ss * self.thirteenth * self.L_f_a * self.sixteenth * self.sixth * self.fourth
        div13 = num13 / den13

        num14 = self.D_eth_a * self.D_th_ss * self.fifth * self.f_th * self.fourteenth * self.R_th * self.SIGMA_eth_ss
        den14 = self.LAMBDA_th_ss * self.thirteenth * self.L_eth_ss * self.L_f_a * self.sixteenth * self.sixth * self.fourth
        div14 = num14 / den14

        num15 = self.first * self.f_th * self.L_eth_ss * self.P_eth_a * self.R_eth * self.R_th * self.SIGMA_eth_ss
        den15 = self.LAMBDA_th_ss * self.L_eth_a * self.thirteenth * self.third * self.fourth
        div15 = num15 / den15

        num16 = self.D_eth_ss * self.nineteenth * self.f_th * self.L_eth_ss * self.P_eth_a * self.R_eth * self.R_th * self.SIGMA_eth_ss;
        den16 = self.LAMBDA_th_ss * self.thirteenth * self.L_f_a * self.third * self.fourth
        div16 = num16 / den16

        num17 = self.Da * self.D_eth_a * self.fifth * self.f_th * self.fourteenth * self.R_eth * self.R_th * self.SIGMA_eth_ss;
        den17 = self.La * self.LAMBDA_th_ss * self.L_eth_a * self.thirteenth * self.sixteenth * self.eighteenth * self.fourth
        div17 = num17 / den17

        num18 = self.D_eth_a * self.D_th_ss * self.fifth * self.f_th * self.L_th_ss * self.P_eth_a * self.R_eth * self.R_th * self.SIGMA_eth_ss
        den18 = self.LAMBDA_th_ss * self.L_eth_a * self.thirteenth * self.L_eth_ss * self.sixteenth * self.third * self.fourth
        div18 = num18 / den18

        num19 = self.Da * self.D_eth_ss * self.fifth * self.f_th * self.fourteenth * self.R_eth * self.R_th * self.SIGMA_eth_ss;
        den19 = self.La * self.LAMBDA_th_ss * self.thirteenth * self.L_f_a * self.sixteenth * self.third * self.fourth
        div19 = num19 / den19

        num20 = self.D_eth_ss * self.D_th_ss * self.fifth * self.f_th * self.fourteenth * self.R_eth * self.R_th * self.SIGMA_eth_ss;
        den20 = self.LAMBDA_th_ss * self.thirteenth * self.L_eth_ss * self.L_f_a * self.sixteenth * self.eighteenth * self.fourth
        div20 = num20 / den20

        num21 = self.Da * self.D_eth_ss * self.fifth * self.f_th * self.L_th_ss * self.P_eth_a * self.SIGMA_eth_a
        den21 = self.La * self.LAMBDA_th_ss * self.thirteenth * self.L_eth_ss * self.sixteenth * self.sixth * self.fifteenth
        div21 = num21 / den21

        num22 = self.Da * self.D_eth_ss * self.fifth * self.f_th * self.fourteenth * self.SIGMA_eth_a;
        den22 = self.LAMBDA_th_ss * self.L_eth_a * self.thirteenth * self.L_eth_ss * self.sixteenth * self.sixth * self.fifteenth
        div22 = num22 / den22

        num23 = self.Da * self.D_eth_a * self.fifth * self.f_th * self.fourteenth * self.SIGMA_eth_a;
        den23 = self.La * self.LAMBDA_th_ss * self.thirteenth * self.L_f_a * self.sixteenth * self.sixth * self.fifteenth
        div23 = num23 / den23

        num24 = self.Da * self.D_eth_a * self.fifth * self.f_th * self.fourteenth * self.SIGMA_eth_a;
        den24 = self.LAMBDA_th_ss * self.L_eth_a * self.thirteenth * self.L_f_a * self.sixteenth * self.sixth * self.fifteenth
        div24 = num24 / den24

        num25 = self.Da * self.D_eth_ss * self.fifth * self.f_th * self.fourteenth * self.R_eth * self.SIGMA_eth_a
        den25 = self.La * self.LAMBDA_th_ss * self.thirteenth * self.L_eth_ss * self.sixteenth * self.third * self.fifteenth
        div25 = num25 / den25

        num26 = self.Da * self.D_eth_ss * self.fifth * self.f_th * self.fourteenth * self.R_eth * self.SIGMA_eth_a
        den26 = self.LAMBDA_th_ss * self.L_eth_a * self.thirteenth * self.L_eth_ss * self.sixteenth * self.third * self.fifteenth
        div26 = num26 / den26

        num27 = self.Da * self.D_eth_ss * self.fifth * self.f_th * self.fourteenth * self.R_eth * self.SIGMA_eth_a
        den27 = self.La * self.LAMBDA_th_ss * self.thirteenth * self.L_f_a * self.sixteenth * self.third * self.fifteenth
        div27 = num27 / den27

        num28 = self.Da * self.D_eth_ss * self.fifth * self.f_th * self.fourteenth * self.R_eth * self.SIGMA_eth_a
        den28 = self.LAMBDA_th_ss * self.L_eth_a * self.thirteenth * self.L_f_a * self.sixteenth * self.third * self.fifteenth
        div28 = num28 / den28

        num29 = self.Da * self.fifth * self.f_th * self.L_th_ss * self.P_eth_a * self.S_eth_a;
        den29 = self.La * self.LAMBDA_th_ss * self.sixteenth * self.sixth * self.twentieth
        div29 = num29 / den29

        num30 = self.Da * self.fifth * self.f_th * self.fourteenth * self.S_eth_a
        den30 = self.LAMBDA_th_ss * self.L_f_a * self.sixteenth * self.sixth * self.twentieth
        div30 = num30 / den30

        total = div1 + div2 + div3 - div4 - div5 + div6 - div7 - div8 + div9 + div10 - div11 - div12 - div13 - div14 - div15 - div16 + div17 + div18 + div19 + div20 - div21 + div22 + div23 - div24 + div25 - div26 - div27 + div28 + div29 + div30

        s["NeutronTerm"] = (self.shielding_factor * total) / self.Zs

        # Calculate neut_const_term[i] =  ST[i]*P_mu_n_0/Zs[i]*
            # (first[i]*feth[i]*L_eth_ss[i]*second[i]/
                # (LAMBDA_eth_ss[i]*L_eth_a*thirteenth[i]*sixth[i])+
            # first[i]*feth[i]*L_eth_ss[i]*second[i]/
                # (LAMBDA_eth_ss[i]*thirteenth[i]*L_f_a*sixth[i])+
            # twentysecond[i]*feth[i]*LAMBDA_mu*second[i]/
                # (LAMBDA_eth_ss[i]*third[i])-
            # first[i]*feth[i]*L_eth_ss[i]*second[i]*R_eth[i]/
                # (LAMBDA_eth_ss[i]*L_eth_a*thirteenth[i]*third[i])-
            # D_eth_ss[i]*nineteenth[i]*feth[i]*L_eth_ss[i]*second[i]*R_eth[i]/
                # (LAMBDA_eth_ss[i]*thirteenth[i]*L_f_a*third[i])+
            # twentysecond[i]*f_th[i]*LAMBDA_mu*Math.pow(P_eth_a,2)*R_th[i]*SIGMA_eth_ss[i]/
                # (LAMBDA_th_ss[i]*P_eth_ss[i]*third[i]*seventeenth[i])-
            # D_th_ss[i]*fifth[i]*f_th[i]*L_th_ss[i]*Math.pow(P_eth_a,2)*Math.pow(R_th[i],2)*SIGMA_eth_ss[i]/
                # (Math.pow(LAMBDA_th_ss[i],2)*sixteenth[i]*P_eth_ss[i]*third[i]*seventeenth[i])-
            # Da*fifth[i]*f_th[i]*L_th_ss[i]*Math.pow(P_eth_a,2)*Math.pow(R_th[i],2)*SIGMA_eth_ss[i]/
                # (La*LAMBDA_th_ss[i]*sixteenth[i]*P_eth_ss[i]*third[i]*seventeenth[i])+
            # first[i]*f_th[i]*L_eth_ss[i]*Math.pow(P_eth_a,2)*R_th[i]*SIGMA_eth_ss[i]/
                # (LAMBDA_th_ss[i]*L_eth_a*thirteenth[i]*P_eth_ss[i]*R_eth[i]*sixth[i]*fourth[i])+
            # first[i]*f_th[i]*L_eth_ss[i]*Math.pow(P_eth_a,2)*R_th[i]*SIGMA_eth_ss[i]/
                # (LAMBDA_th_ss[i]*thirteenth[i]*L_f_a*P_eth_ss[i]*R_eth[i]*sixth[i]*fourth[i])-
            # Da*D_eth_a*fifth[i]*f_th[i]*L_th_ss[i]*Math.pow(P_eth_a,2)*Math.pow(R_th[i],2)*SIGMA_eth_ss[i]/
                # (La*LAMBDA_th_ss[i]*L_eth_a*thirteenth[i]*sixteenth[i]*P_eth_ss[i]*R_eth[i]*sixth[i]*fourth[i])-
            # D_eth_a*D_th_ss[i]*fifth[i]*f_th[i]*L_th_ss[i]*Math.pow(P_eth_a,2)*Math.pow(R_th[i],2)*SIGMA_eth_ss[i]/
                # (LAMBDA_th_ss[i]*L_eth_a*thirteenth[i]*L_eth_ss[i]*sixteenth[i]*P_eth_ss[i]*R_eth[i]*sixth[i]*fourth[i])-
            # Da*D_eth_a*fifth[i]*f_th[i]*L_th_ss[i]*Math.pow(P_eth_a,2)*Math.pow(R_th[i],2)*SIGMA_eth_ss[i]/
                # (La*LAMBDA_th_ss[i]*thirteenth[i]*L_f_a*sixteenth[i]*P_eth_ss[i]*R_eth[i]*sixth[i]*fourth[i])-
            # D_eth_a*D_th_ss[i]*fifth[i]*f_th[i]*L_th_ss[i]*Math.pow(P_eth_a,2)*Math.pow(R_th[i],2)*SIGMA_eth_ss[i]/
                # (LAMBDA_th_ss[i]*thirteenth[i]*L_eth_ss[i]*L_f_a*sixteenth[i]*P_eth_ss[i]*R_eth[i]*sixth[i]*fourth[i])-
            # first[i]*f_th[i]*L_eth_ss[i]*Math.pow(P_eth_a,2)*R_th[i]*SIGMA_eth_ss[i]/
                # (LAMBDA_th_ss[i]*L_eth_a*thirteenth[i]*P_eth_ss[i]*eighteenth[i]*fourth[i])-
            # D_eth_ss[i]*nineteenth[i]*f_th[i]*L_eth_ss[i]*Math.pow(P_eth_a,2)*R_th[i]*SIGMA_eth_ss[i]/
                # (LAMBDA_th_ss[i]*thirteenth[i]*L_f_a*P_eth_ss[i]*eighteenth[i]*fourth[i])+
            # Da*D_eth_a*fifth[i]*f_th[i]*L_th_ss[i]*Math.pow(P_eth_a,2)*Math.pow(R_th[i],2)*SIGMA_eth_ss[i]/
                # (La*LAMBDA_th_ss[i]*L_eth_a*thirteenth[i]*sixteenth[i]*P_eth_ss[i]*third[i]*fourth[i])+
            # D_eth_a*D_th_ss[i]*fifth[i]*f_th[i]*L_th_ss[i]*Math.pow(P_eth_a,2)*Math.pow(R_th[i],2)*SIGMA_eth_ss[i]/
                # (LAMBDA_th_ss[i]*L_eth_a*thirteenth[i]*L_eth_ss[i]*sixteenth[i]*P_eth_ss[i]*third[i]*fourth[i])+
            # Da*D_eth_ss[i]*fifth[i]*f_th[i]*L_th_ss[i]*Math.pow(P_eth_a,2)*Math.pow(R_th[i],2)*SIGMA_eth_ss[i]/
                # (La*LAMBDA_th_ss[i]*thirteenth[i]*L_f_a*sixteenth[i]*P_eth_ss[i]*third[i]*fourth[i])+
            # D_eth_ss[i]*D_th_ss[i]*fifth[i]*f_th[i]*L_th_ss[i]*Math.pow(P_eth_a,2)*Math.pow(R_th[i],2)*SIGMA_eth_ss[i]/
                # (LAMBDA_th_ss[i]*thirteenth[i]*L_eth_ss[i]*L_f_a*sixteenth[i]*P_eth_ss[i]*eighteenth[i]*fourth[i])-
            # Da*D_eth_ss[i]*fifth[i]*f_th[i]*L_th_ss[i]*Math.pow(P_eth_a,2)*R_th[i]*SIGMA_eth_a/
                # (La*LAMBDA_th_ss[i]*thirteenth[i]*L_eth_ss[i]*sixteenth[i]*P_eth_ss[i]*R_eth[i]*sixth[i]*fifteenth[i])+
            # Da*D_eth_ss[i]*fifth[i]*f_th[i]*L_th_ss[i]*Math.pow(P_eth_a,2)*R_th[i]*SIGMA_eth_a/
                # (LAMBDA_th_ss[i]*L_eth_a*thirteenth[i]*L_eth_ss[i]*sixteenth[i]*P_eth_ss[i]*R_eth[i]*sixth[i]*fifteenth[i])+
            # Da*D_eth_a*fifth[i]*f_th[i]*L_th_ss[i]*Math.pow(P_eth_a,2)*R_th[i]*SIGMA_eth_a/
                # (La*LAMBDA_th_ss[i]*thirteenth[i]*L_f_a*sixteenth[i]*P_eth_ss[i]*R_eth[i]*sixth[i]*fifteenth[i])-
            # Da*D_eth_a*fifth[i]*f_th[i]*L_th_ss[i]*Math.pow(P_eth_a,2)*R_th[i]*SIGMA_eth_a/
                # (LAMBDA_th_ss[i]*L_eth_a*thirteenth[i]*L_f_a*sixteenth[i]*P_eth_ss[i]*R_eth[i]*sixth[i]*fifteenth[i])+
            # Da*D_eth_ss[i]*fifth[i]*f_th[i]*L_th_ss[i]*Math.pow(P_eth_a,2)*R_th[i]*SIGMA_eth_a/
            # (La*LAMBDA_th_ss[i]*thirteenth[i]*L_eth_ss[i]*sixteenth[i]*P_eth_ss[i]*eighteenth[i]*fifteenth[i])-
            # Da*D_eth_ss[i]*fifth[i]*f_th[i]*L_th_ss[i]*Math.pow(P_eth_a,2)*R_th[i]*SIGMA_eth_a/
                # (LAMBDA_th_ss[i]*L_eth_a*thirteenth[i]*L_eth_ss[i]*sixteenth[i]*P_eth_ss[i]*third[i]*fifteenth[i])-
            # Da*D_eth_ss[i]*fifth[i]*f_th[i]*L_th_ss[i]*Math.pow(P_eth_a,2)*R_th[i]*SIGMA_eth_a/
                # (La*LAMBDA_th_ss[i]*thirteenth[i]*L_f_a*sixteenth[i]*P_eth_ss[i]*third[i]*fifteenth[i])+
            # Da*D_eth_ss[i]*fifth[i]*f_th[i]*L_th_ss[i]*Math.pow(P_eth_a,2)*R_th[i]*SIGMA_eth_a/
                # (LAMBDA_th_ss[i]*L_eth_a*thirteenth[i]*L_f_a*sixteenth[i]*P_eth_ss[i]*eighteenth[i]*fifteenth[i])+
            # Da*fifth[i]*f_th[i]*L_th_ss[i]*Math.pow(P_eth_a,2)*R_th[i]*S_eth_a/
                # (La*LAMBDA_th_ss[i]*sixteenth[i]*P_eth_ss[i]*R_eth[i]*sixth[i]*twentyfirst[i])+
            # Da*fifth[i]*f_th[i]*L_th_ss[i]*Math.pow(P_eth_a,2)*R_th[i]*S_eth_a/
                # (LAMBDA_th_ss[i]*L_f_a*sixteenth[i]*P_eth_ss[i]*R_eth[i]*sixth[i]*twentyfirst[i]));

        num1 = self.first * self.f_eth * self.L_eth_ss * self.second;
        den1 = self.LAMBDA_eth_ss * self.L_eth_a * self.thirteenth * self.sixth;
        div1 = num1 / den1

        num2 = self.first * self.f_eth * self.L_eth_ss * self.second;
        den2 = self.LAMBDA_eth_ss * self.thirteenth * self.L_f_a * self.sixth;
        div2 = num2 / den2

        num3 = self.twentysecond * self.f_eth * self.LAMBDA_mu * self.second;
        den3 = self.LAMBDA_eth_ss * self.third;
        div3 = num3 / den3

        num4 = self.first * self.f_eth * self.L_eth_ss * self.second * self.R_eth
        den4 = self.LAMBDA_eth_ss * self.L_eth_a * self.thirteenth * self.third;
        div4 = num4 / den4

        num5 = self.D_eth_ss * self.nineteenth * self.f_eth * self.L_eth_ss * self.second * self.R_eth;
        den5 = self.LAMBDA_eth_ss * self.thirteenth * self.L_f_a * self.third;
        div5 = num5 / den5

        pow6 = self.P_eth_a**2.0
        num6 = self.twentysecond * self.f_th * self.LAMBDA_mu * pow6 * self.R_th * self.SIGMA_eth_ss;
        den6 = self.LAMBDA_th_ss * self.P_eth_ss * self.third * self.seventeenth;
        div6 = num6 / den6

        pow7a = self.R_th**2.0
        num7  = self.D_th_ss * self.fifth * self.f_th * self.L_th_ss * pow6 * pow7a * self.SIGMA_eth_ss
        pow7b = self.LAMBDA_th_ss**2.0
        den7  = pow7b * self.sixteenth * self.P_eth_ss * self.third * self.seventeenth
        div7  = num7 / den7

        num8 = self.Da * self.fifth * self.f_th * self.L_th_ss * pow6 * pow7a * self.SIGMA_eth_ss
        den8 = self.La * self.LAMBDA_th_ss * self.sixteenth * self.P_eth_ss * self.third * self.seventeenth;
        div8 = num8 / den8

        num9 = self.first * self.f_th * self.L_eth_ss * pow6 * self.R_th * self.SIGMA_eth_ss;
        den9 = self.LAMBDA_th_ss * self.L_eth_a * self.thirteenth * self.P_eth_ss * self.R_eth * self.sixth * self.fourth
        div9 = num9 / den9

        num10 = self.first * self.f_th * self.L_eth_ss * pow6 * self.R_th * self.SIGMA_eth_ss;
        den10 = self.LAMBDA_th_ss * self.thirteenth * self.L_f_a * self.P_eth_ss * self.R_eth * self.sixth * self.fourth
        div10 = num10 / den10

        num11 = self.Da * self.D_eth_a * self.fifth * self.f_th * self.L_th_ss * pow6 * pow7a * self.SIGMA_eth_ss;
        den11 = self.La * self.LAMBDA_th_ss * self.L_eth_a * self.thirteenth * self.sixteenth * self.P_eth_ss * self.R_eth * self.sixth * self.fourth
        div11 = num11 / den11

        num12 = self.D_eth_a * self.D_th_ss * self.fifth * self.f_th * self.L_th_ss * pow6 * pow7a * self.SIGMA_eth_ss;
        den12 = self.LAMBDA_th_ss * self.L_eth_a * self.thirteenth * self.L_eth_ss * self.sixteenth * self.P_eth_ss * self.R_eth * self.sixth * self.fourth
        div12 = num12 / den12

        num13 = self.Da * self.D_eth_a * self.fifth * self.f_th * self.L_th_ss * pow6 * pow7a * self.SIGMA_eth_ss;
        den13 = self.La * self.LAMBDA_th_ss * self.thirteenth * self.L_f_a * self.sixteenth * self.P_eth_ss * self.R_eth * self.sixth * self.fourth
        div13 = num13 / den13

        num14 = self.D_eth_a * self.D_th_ss * self.fifth * self.f_th * self.L_th_ss * pow6 * pow7a * self.SIGMA_eth_ss;
        den14 = self.LAMBDA_th_ss * self.thirteenth * self.L_eth_ss * self.L_f_a * self.sixteenth * self.P_eth_ss * self.R_eth * self.sixth * self.fourth
        div14 = num14 / den14

        num15 = self.first * self.f_th * self.L_eth_ss * pow6 * self.R_th * self.SIGMA_eth_ss;
        den15 = self.LAMBDA_th_ss * self.L_eth_a * self.thirteenth * self.P_eth_ss * self.eighteenth * self.fourth;
        div15 = num15 / den15

        num16 = self.D_eth_ss * self.nineteenth * self.f_th * self.L_eth_ss * pow6 * self.R_th * self.SIGMA_eth_ss
        den16 = self.LAMBDA_th_ss * self.thirteenth * self.L_f_a * self.P_eth_ss * self.eighteenth * self.fourth;
        div16 = num16 / den16

        num17 = self.Da * self.D_eth_a * self.fifth * self.f_th * self.L_th_ss * pow6 * pow7a * self.SIGMA_eth_ss;
        den17 = self.La * self.LAMBDA_th_ss * self.L_eth_a * self.thirteenth * self.sixteenth * self.P_eth_ss * self.third * self.fourth;
        div17 = num17 / den17

        num18 = self.D_eth_a * self.D_th_ss * self.fifth * self.f_th * self.L_th_ss * pow6 * pow7a * self.SIGMA_eth_ss;
        den18 = self.LAMBDA_th_ss * self.L_eth_a * self.thirteenth * self.L_eth_ss * self.sixteenth * self.P_eth_ss * self.third * self.fourth;
        div18 = num18 / den18

        num19 = self.Da * self.D_eth_ss * self.fifth * self.f_th * self.L_th_ss * pow6 * pow7a * self.SIGMA_eth_ss;
        den19 = self.La * self.LAMBDA_th_ss * self.thirteenth * self.L_f_a * self.sixteenth * self.P_eth_ss * self.third * self.fourth;
        div19 = num19 / den19

        num20 = self.D_eth_ss * self.D_th_ss * self.fifth * self.f_th * self.L_th_ss * pow6 * pow7a * self.SIGMA_eth_ss;
        den20 = self.LAMBDA_th_ss * self.thirteenth * self.L_eth_ss * self.L_f_a * self.sixteenth * self.P_eth_ss * self.eighteenth * self.fourth;
        div20 = num20 / den20

        num21 = self.Da * self.D_eth_ss * self.fifth * self.f_th * self.L_th_ss * pow6 * self.R_th * self.SIGMA_eth_a;
        den21 = self.La * self.LAMBDA_th_ss * self.thirteenth * self.L_eth_ss * self.sixteenth * self.P_eth_ss * self.R_eth * self.sixth * self.fifteenth
        div21 = num21 / den21

        num22 = self.Da * self.D_eth_ss * self.fifth * self.f_th * self.L_th_ss * pow6 * self.R_th * self.SIGMA_eth_a;
        den22 = self.LAMBDA_th_ss * self.L_eth_a * self.thirteenth * self.L_eth_ss * self.sixteenth * self.P_eth_ss * self.R_eth * self.sixth * self.fifteenth
        div22 = num22 / den22

        num23 = self.Da * self.D_eth_a * self.fifth * self.f_th * self.L_th_ss * pow6 * self.R_th * self.SIGMA_eth_a;
        den23 = self.La * self.LAMBDA_th_ss * self.thirteenth * self.L_f_a * self.sixteenth * self.P_eth_ss * self.R_eth * self.sixth * self.fifteenth
        div23 = num23 / den23

        num24 = self.Da * self.D_eth_a * self.fifth * self.f_th * self.L_th_ss * pow6 * self.R_th * self.SIGMA_eth_a;
        den24 = self.LAMBDA_th_ss * self.L_eth_a * self.thirteenth * self.L_f_a * self.sixteenth * self.P_eth_ss * self.R_eth * self.sixth * self.fifteenth
        div24 = num24 / den24

        num25 = self.Da * self.D_eth_ss * self.fifth * self.f_th * self.L_th_ss * pow6 * self.R_th * self.SIGMA_eth_a;
        den25 = self.La * self.LAMBDA_th_ss * self.thirteenth * self.L_eth_ss * self.sixteenth * self.P_eth_ss * self.eighteenth * self.fifteenth;
        div25 = num25 / den25

        num26 = self.Da * self.D_eth_ss * self.fifth * self.f_th * self.L_th_ss * pow6 * self.R_th * self.SIGMA_eth_a;
        den26 = self.LAMBDA_th_ss * self.L_eth_a * self.thirteenth * self.L_eth_ss * self.sixteenth * self.P_eth_ss * self.third * self.fifteenth;
        div26 = num26 / den26

        num27 = self.Da * self.D_eth_ss * self.fifth * self.f_th * self.L_th_ss * pow6 * self.R_th * self.SIGMA_eth_a;
        den27 = self.La * self.LAMBDA_th_ss * self.thirteenth * self.L_f_a * self.sixteenth * self.P_eth_ss * self.third * self.fifteenth;
        div27 = num27 / den27

        num28 = self.Da * self.D_eth_ss * self.fifth * self.f_th * self.L_th_ss * pow6 * self.R_th * self.SIGMA_eth_a;
        den28 = self.LAMBDA_th_ss * self.L_eth_a * self.thirteenth * self.L_f_a * self.sixteenth * self.P_eth_ss * self.eighteenth * self.fifteenth;
        div28 = num28 / den28

        num29 = self.Da * self.fifth * self.f_th * self.L_th_ss * pow6 * self.R_th * self.S_eth_a
        den29 = self.La * self.LAMBDA_th_ss * self.sixteenth * self.P_eth_ss * self.R_eth * self.sixth * self.twentyfirst
        div29 = num29 / den29

        num30 = self.Da * self.fifth * self.f_th * self.L_th_ss * pow6 * self.R_th * self.S_eth_a
        den30 = self.LAMBDA_th_ss * self.L_f_a * self.sixteenth * self.P_eth_ss * self.R_eth * self.sixth * self.twentyfirst
        div30 = num30 / den30

        total = div1 + div2 + div3 - div4 - div5 + div6 - div7 - div8 + div9 + div10 - div11 - div12 - div13 - div14 - div15 - div16 + div17 + div18 + div19 + div20 - div21 + div22 + div23 - div24 + div25 - div26 - div27 + div28 + div29 + div30;

        s["FastMuonTerm"] = (self.shielding_factor * 5.8E-6 * self.Yf * self.phi_mu_f0 * total) / self.Zs

    def calculateTimesteppingCoeffs(self, s):
        # This is getting tricky.  The NeutronCalib terms are the same whether
        # a time averaging or time stepping procedure is used.  This calculation
        # however is different depending on the type of procedure.  Here I will
        # calculate the Time Averaged coefficients.  Hopefully can generalise
        # to time stepping later.

        norm_factor = 1e+24

        # initialize (first time step) or read in coefficients
        if s["age"] == self.experiment["timestep"]:

            s["psi_ca_0_coeff"]         = 0.0
            s["psi_k_0_coeff"]          = 0.0
            s["Pf_0_coeff"]             = 0.0
            s["FastMuonContrib"]        = 0.0
            s["SlowMuonContrib"]        = 0.0

            # Initial RHS_1 == Inv_c (or Inv_m - Inv_r)
            s["RHS_1"] = (self.ClCalc * self.ClRatio * 0.000000000000001) - s["nucleogenic inventory"]

        # Calculate some intermediate terms
        exp1 = math.exp(-(self.LAMBDA_36) * s["age"])
        pro1 = -1.0 * self.LAMBDA_36 * self.experiment["timestep"]
        min1 = 1 - math.exp(pro1)
        div1 = min1 / self.LAMBDA_36
        mul1 = self.S_el * div1 * exp1
        mul2 = self.shielding_factor * self.Q_s * self.CaCalc / norm_factor
        mul3 = self.shielding_factor * self.Q_s * self.KCalc / norm_factor

        # norm_factor is there because psi_ca_0_coeff, psi_k_0_coeff and Pf_0_coeff are
        # the terms involved in the calibration and the first two terms are 22 orders
        # of magnitude larger than the third.  
        # Prior results show that results are insensitive to norm_factor for up to ten
        # orders of magnitude.  Probably a result of using double precision in original
        # java code, as it was never an issue in machine precision independent mathematica

        s["psi_ca_0_coeff"] += mul1 * mul2
        s["psi_k_0_coeff"] += mul1 * mul3
        s["Pf_0_coeff"] += self.S_th * div1 * exp1 * s["NeutronTerm"]
        s["FastMuonContrib"] += self.S_mu * div1 * exp1 * s["FastMuonTerm"]
        s["SlowMuonContrib"] += self.S_mu * div1 * exp1 * self.Q_mu * self.Pmu_0 * self.shielding_factor

        # Calculate RHS below.  Note that this is really
        # RHS = InvC - FastMuonContrib - SlowMuonContrib
        # As it appears in the time averaing procedure (OutputFor36clCalibration)
        # but from time step to time step it takes away the individual contribution from
        # that time step
        s["RHS_1"] -= self.S_mu * div1 * exp1 * s["FastMuonTerm"]
        s["RHS_1"] -= self.S_mu * div1 * exp1 * self.Q_mu * self.Pmu_0 * self.shielding_factor

# vim: ts=4:sw=4:et
