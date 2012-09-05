"""
LiftonScalingFunctions.py

Copyright (c) 2006-2007 University of Colorado. All rights reserved.

Lifton doi : 10.1016/j.epsl.2005.07.001
"""

from ACE.Framework.Component import Component

import math

class LiftonScalingFunctions(Component):
    def __init__(self, collections, workflow):
        super(LiftonScalingFunctions, self).__init__(collections, workflow)
        self.constants = collections.get("constants")
        self.values = collections.get("sunspots")

        self.dorman_th_1 = 9.694
        self.dorman_th_2 = 0.9954

    def __call__(self, samples):
        for s in samples:
            s["df_th"] = self.calculateDormanFunction(s["rigidity"], self.dorman_th_1, self.dorman_th_2)

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
        # Calculate Equation 4 of Lifton 2005 doi ref above

        self.b1 = 9.8313E-01
        self.b2 = 1.6038E-03
        self.b3 = 1.9988E+00
        self.c1 = 1.8399
        self.c2 = -1.1854E+02
        self.c3 = -4.9420E-02
        self.c4 = 8.0139E-01
        self.c5 = 1.2708E-04
        self.c6 = 9.4647E-01
        self.c7 = -3.2208E-02
        self.c8 = 1.2688

        # First get appropriate sunspot number S for age
        age = s["age"]

        if age <= 11300:
            sunspot = self.getInterpolatedSunspotnumber(age)
            num = self.b1 * (3.0 - self.b2 * sunspot)**2.0
            den = (3.0) ** self.b3
            S = num / den

        if age > 11300:
            S = 0.950

        # Need X, the atmospheric depth
        pressure = s["atmospheric pressure"]
        X = pressure

        # Now just need the cutoff rigidity
        Rc = s["rigidity"]

        # Now calculate Equation 4.  Term by term

        term1 = self.c1 * math.log(X * S)
        arg1 = self.c2 * S / (( Rc + 5.0 * S)**(2.0 * S))
        term2 = -1.0 * S * math.exp(arg1)

        term3 = self.c3 * X**self.c4

        term4 = self.c5 * ((Rc + 4.0 * S) * X)**self.c6

        term5 = self.c7 * (Rc + 4.0 * S)**self.c8

        logIn = term1 + term2 + term3 + term4 + term5

        s["S_sp"] = math.exp(logIn)

    def setScalingFunctionTH(self, s):

        # Advice from Nat was to leave neutrons alone at this stage.
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

        self.a1 = 5.1132
        self.a2 = -8.8225E-3
        self.a3 = 3.7346E-6
        self.a4 = 7.9712E-5
        self.a5 = -7.5605E-2
        self.a6 = -1.3203E-3

        # calculate Equation 2 of Lifton 2005 for slow muons
        pressure = s["atmospheric pressure"]
        X = pressure

        # Now just need the cutoff rigidity
        Rc = s["rigidity"]

        first = self.a1 + self.a2 * X + self.a3 * X**2 
        second =  self.a4 * X * Rc + self.a5 * Rc + self.a6 * Rc**2
        sum = first + second

        s["S_mu"] = math.exp(sum)

    def setScalingFunctionMUfast(self, s):

        # fast muon scaling
        # Table 1 doi in header
        self.a1 = 2.4424
        self.a2 = -2.8717E-3
        self.a3 = 4.7441E-7
        self.a4 = 4.3045E-5
        self.a5 = -3.7891E-2
        self.a6 = -7.6795E-4

        df_mu    = s["df_mu"]
        pressure = s["atmospheric pressure"]
        X = pressure

        Rc = s["rigidity"]

        first = self.a1 + self.a2 * X + self.a3 * X**2
        second =  self.a4 * X * Rc + self.a5 * Rc + self.a6 * Rc**2
        sum = first + second

        s["S_mu_fast"] = math.exp(sum)

    def getInterpolatedSunspotnumber(self, age):
        keys = self.values.keys()
        keys.sort()

        A    = None
        B    = None
        i    = 0

        while i < (len(keys) - 1):
            A = keys[i]
            B = keys[i+1]

            if ((A <= age) and (age < B)):
                break

            i = i + 1

        #print "Age:" + str(age)
        #print "A:" + str(A)
        #print "B:" + str(B)

        # calculate A_int + (age - A) * ((B_int - A_int)/(B -A))
        A_int = self.values[A]['sunspots']
        B_int = self.values[B]['sunspots']

        int_diff  = B_int - A_int
        age_diff  = B - A
        targ_diff = age - A

        div     = int_diff / age_diff
        product = targ_diff * div

        return A_int + product

# vim: ts=4:sw=4:et
