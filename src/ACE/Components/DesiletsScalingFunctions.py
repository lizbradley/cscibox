"""
DesiletsScalingFunctions.py

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

class DesiletsScalingFunctions(Component):
    def __init__(self, collections, workflow):
        super(DesiletsScalingFunctions, self).__init__(collections, workflow)
        self.constants = collections.get("Constants")

        self.dorman_sp_1 = 10.275
        self.dorman_sp_2 = 0.9615
        self.dorman_th_1 = 9.694
        self.dorman_th_2 = 0.9954
        self.dorman_mu_1 = 38.5
        self.dorman_mu_2 = 1.0

    def __call__(self, samples):
        for s in samples:
            s["df_sp"] = self.calculateDormanFunction(s["rigidity"], self.dorman_sp_1, self.dorman_sp_2)
            s["df_th"] = self.calculateDormanFunction(s["rigidity"], self.dorman_th_1, self.dorman_th_2)
            s["df_mu"] = self.calculateDormanFunction(s["rigidity"], self.dorman_mu_1, self.dorman_mu_2)

            self.setScalingFunctionSP(s)
            self.setScalingFunctionTH(s)
            self.setScalingFunctionMU(s)
            self.setScalingFunctionMUfast(s)

        return (([self.get_connection()], samples),)

    def calculateDormanFunction(self, rigidity, dorman1, dorman2):
        dorman1 = -dorman1
        dorman2 = -dorman2

        pow1 = rigidity**dorman2
        product = dorman1 * pow1

        e = math.exp(product)

        return 1.0 - e

    def setScalingFunctionSP(self, s):
        # calculate the following formula
        # df_sp*
        #
        # EXP(
        # (1033-pressure)/
        # (
        # (1033.1-pressure)/
        # (
        # (
        # (n*(1+EXP(-a*rigidity^-k))^-1)*1033.1+
        # 0.5*(b_0+b_1*rigidity+b_2*rigidity^2)*1033.1^2+
        # (1/3)*(b_3+b_4*rigidity+b_5*rigidity^2)*1033.1^3+
        # 0.25*(b_6+b_7*rigidity+b_8*rigidity^2)*1033.1^4
        # )-
        # (
        # (n*(1+EXP(-a*rigidity^-k))^-1)*pressure+
        # 0.5*(b_0+b_1*rigidity+b_2*rigidity^2)*pressure^2+
        # (1/3)*(b_3+b_4*rigidity+b_5*rigidity^2)*pressure^3+
        # 0.25*(b_6+b_7*rigidity+b_8*rigidity^2)*pressure^4
        # )
        # )
        # )
        # )

        df_sp    = s["df_sp"]

        ten33     = 1033.0

        a   = self.constants["a"]
        k   = self.constants["K"]
        n   = self.constants["n"]

        pressure = s["atmospheric pressure"]
        pressure2 = pressure**2.0
        pressure3 = pressure**3.0
        pressure4 = pressure**4.0

        rigidity  = s["rigidity"]
        rigidity2 = rigidity**2.0

        ten33one  = 1033.1
        ten33one2 = ten33one**2.0
        ten33one3 = ten33one**3.0
        ten33one4 = ten33one**4.0

        # calculate (1033-pressure)
        sub1 = ten33 - pressure

        # calculate (1033.1-pressure)
        sub2 = ten33one - pressure

        # calculate (n*(1+EXP(-a*rigidity^-k))^-1)
        product1 = (-a) * (rigidity**(-k))
        exp1     = math.exp(product1)
        sum1     = 1 + exp1
        sum1POW  = sum1**-1.0
        nProduct = n * sum1POW

        # calculate (n*(1+EXP(-a*rigidity^-k))^-1)*1033.1
        nProductCon = nProduct* ten33one

        # calculate (n*(1+EXP(-a*rigidity^-k))^-1)*pressure
        nProductP = nProduct * pressure

        # calculate (b_0+b_1*rigidity+b_2*rigidity^2)
        b0sum     = self.constants["b0"] + (self.constants["b1"] * rigidity) + (self.constants["b2"] * rigidity2)

        # calculate (b_3+b_4*rigidity+b_5*rigidity^2)
        b3sum     = self.constants["b3"] + (self.constants["b4"] * rigidity) + (self.constants["b5"] * rigidity2)

        # calculate (b_6+b_7*rigidity+b_8*rigidity^2)
        b6sum     = self.constants["b6"] + (self.constants["b7"] * rigidity) + (self.constants["b8"] * rigidity2)

        # calculate 0.25*(b_6+b_7*rigidity+b_8*rigidity^2)*pressure^4
        quarterProductP = 0.25 * b6sum * pressure4

        # calculate 0.25*(b_6+b_7*rigidity+b_8*rigidity^2)*1033.1^4
        quarterProductCon = 0.25 * b6sum * ten33one4

        # calculate (1/3)*(b_3+b_4*rigidity+b_5*rigidity^2)*pressure^3
        thirdProductP = (1.0 / 3.0) * b3sum * pressure3

        # calculate (1/3)*(b_3+b_4*rigidity+b_5*rigidity^2)*1033.1^3
        thirdProductCon = (1.0 / 3.0) * b3sum * ten33one3

        # calculate 0.5*(b_0+b_1*rigidity+b_2*rigidity^2)*pressure^2
        halfProductP = 0.5 * b0sum * pressure2

        # calculate 0.5*(b_0+b_1*rigidity+b_2*rigidity^2)*1033.1^2
        halfProductCon = 0.5 * b0sum * ten33one2

        # add up the previous terms involving the constant
        nSumCon = nProductCon + halfProductCon + thirdProductCon + quarterProductCon
        # System.out.println("nSumCon: " + nSumCon);

        # add up the previous terms involving pressure
        nSumP = nProductP + halfProductP + thirdProductP + quarterProductP
        # System.out.println("nSumP: " + nSumP);

        # compute the difference between the two sums
        ConPressureSub = nSumCon - nSumP
        # System.out.println("ConPressureSub: " + ConPressureSub);

        # compute the first fraction
        div1 = sub2 / ConPressureSub
        # System.out.println("sub2: " + sub2);
        # System.out.println("div1: " + div1);

        # compute the second fraction
        div2 = sub1 / div1
        # System.out.println("sub1: " + sub1);
        # System.out.println("div2: " + div2);

        # take e to the power of the second fraction
        # System.out.println("Math.exp(div2): " + Math.exp(div2.doubleValue()));
        mainEXP = math.exp(div2);

        # at long last compute the result
        s["S_sp"] = df_sp * mainEXP

    def setScalingFunctionTH(self, s):

        # calculate
        # df_th *
        # EXP(
        # (1033-pressure)/
        # (
        # (1033.1-pressure)/
        # (
        # (c_0+c_1*rigidity+c_2*rigidity^2)*1033.1+
        # 0.5*(c_3+c_4*rigidity)*1033.1^2+
        # (1/3)*(c_5+c_6*rigidity)*1033.1^3+
        # 0.25*(c_7+c_8*rigidity)*1033.1^4 -
        #
        # (
        # (c_0+c_1*rigidity+c_2*rigidity^2)*pressure+
        # 0.5*(c_3+c_4*rigidity)*pressure^2+
        # (1/3)*(c_5+c_6*rigidity)*pressure^3+
        # 0.25*(c_7+c_8*rigidity)*pressure^4
        # )
        # )
        # )
        # )

        df_th    = s["df_th"]

        pressure  = s["atmospheric pressure"]
        pressure2 = pressure**2.0
        pressure3 = pressure**3.0
        pressure4 = pressure**4.0

        rigidity  = s["rigidity"]
        rigidity2 = rigidity**2.0

        ten33one  = 1033.1
        ten33one2 = ten33one**2.0
        ten33one3 = ten33one**3.0
        ten33one4 = ten33one**4.0

        sub1 = 1033   - pressure
        sub2 = 1033.1 - pressure

        # calculate (c_0+c_1*rigidity+c_2*rigidity^2)
        c0sum     = self.constants["c0"] + (self.constants["c1"] * rigidity) + (self.constants["c2"] * rigidity2)

        # calculate (c_3+c_4*rigidity)
        c3sum     = self.constants["c3"] + (self.constants["c4"] * rigidity)

        # calculate (c_5+c_6*rigidity)
        c5sum     = self.constants["c5"] + (self.constants["c6"] * rigidity)

        # calculate (c_7+c_8*rigidity)
        c7sum     = self.constants["c7"] + (self.constants["c8"] * rigidity)

        # calculate 0.25*(c_7+c_8*rigidity)*pressure^4
        quarterProductP = 0.25 * c7sum * pressure4

        # calculate 0.25*(c_7+c_8*rigidity)*1033.1^4
        quarterProductCon = 0.25 * c7sum * ten33one4

        # calculate (1/3)*(c_5+c_6*rigidity)*pressure^3
        thirdProductP = ( 1.0 / 3.0 ) * c5sum * pressure3

        # calculate (1/3)*(c_5+c_6*rigidity)*1033.1^3
        thirdProductCon = ( 1.0 / 3.0 ) * c5sum * ten33one3

        # calculate 0.5*(c_3+c_4*rigidity)*pressure^2
        halfProductP = 0.5 * c3sum * pressure2

        # calculate 0.5*(c_3+c_4*rigidity)*1033.1^2
        halfProductCon = 0.5 * c3sum* ten33one2

        # calculate (c_0+c_1*rigidity+c_2*rigidity^2)*pressure
        c0ProductP = c0sum * pressure

        # calculate (c_0+c_1*rigidity+c_2*rigidity^2)*1033.1
        c0ProductCon = c0sum * ten33one

        # add up the previous terms involving the constant

        sumCon = c0ProductCon + halfProductCon + thirdProductCon + quarterProductCon
        # System.out.println("sumCon: " + sumCon);

        # add up the previous terms involving pressure
        sumP = c0ProductP + halfProductP + thirdProductP + quarterProductP
        # System.out.println("sumP: " + sumP);

        # compute the difference between the two sums
        ConPressureSub = sumCon - sumP
        # System.out.println("ConPressureSub: " + ConPressureSub);

        # compute the first fraction
        div1 = sub2 / ConPressureSub
        # System.out.println("sub2: " + sub2);
        # System.out.println("div1: " + div1);

        # compute the second fraction
        div2 = sub1 / div1
        # System.out.println("sub1: " + sub1);
        # System.out.println("div2: " + div2);

        # take e to the power of the second fraction
        # System.out.println("Math.exp(div2): " + Math.exp(div2.doubleValue()));
        mainEXP = math.exp(div2)

        # at long last compute the result
        s["S_th"] = df_th * mainEXP

    def setScalingFunctionMU(self, s):
        # calculate df_mu*EXP((1033-pressure)/(233+3.68*rigidity))

        df_mu    = s["df_mu"]
        pressure = s["atmospheric pressure"]
        rigidity = s["rigidity"]

        # calculate EXP((1033-pressure)/(233+3.68*rigidity))

        denominator = 233.0 + (3.68 * rigidity)
        numerator   = 1033.0 - pressure
        quotient    = numerator / denominator
        term        = math.exp(quotient)

        s["S_mu"] = df_mu * term

    def setScalingFunctionMUfast(self, s):
        # Scaling for fast muons

        df_mu    = s["df_mu"]
        pressure = s["atmospheric pressure"]
        rigidity = s["rigidity"]

        # calculate df_mu*EXP((1033-pressure)/(a0+a1*rigidity+pressure*
        #				 (a2*rigidity+a3))
        # Equation 6 doi:10.1016/S0012-821X(02)01088-9
                
        df_mu    = s["df_mu"]
        pressure = s["atmospheric pressure"]
        rigidity = s["rigidity"]
    
        denominator = 216.58 + 8.783 * rigidity + pressure * (-1.3532E-3 * rigidity + 0.37859) 
        numerator   = 1033.0 - pressure
        quotient    = numerator / denominator
        term        = math.exp(quotient)

        s["S_mu_fast"] = df_mu * term

# vim: ts=4:sw=4:et
