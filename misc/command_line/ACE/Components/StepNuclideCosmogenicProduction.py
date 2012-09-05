"""
StepNuclideCosmogenicProduction.py

Copyright (c) 2006-2007 University of Colorado. All rights reserved.
"""

from ACE.Framework.Component import Component

import math

class StepNuclideCosmogenicProduction(Component):
    def __init__(self, collections, workflow):
        super(StepNuclideCosmogenicProduction, self).__init__(collections, workflow)
        self.constants = collections.get("constants")

        self.LAMBDA_f  = self.constants["LAMBDA_f"]
        self.LAMBDA_mu = self.constants["LAMBDA_mu"]

    def init_sample(self, s):
        self.shielding_factor = s["shielding factor"]

    def __call__(self, samples):
        for s in samples:
            self.init_sample(s)

            self.calculateZs(s);
            self.calculateQ_s(s);
            self.calculateQ_mu(s);
            self.calculateP_sp_ca(s);
            self.calculateP_mu(s);
            self.calculateP_total(s);

        return (([self.get_connection()], samples),)

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

    def calculateP_sp_ca(self, s):
        pass

    def calculateP_mu(self, s):
        pass

    def calculateP_total(self, s):
        # calculate P_sp_ca+P_mu
        s["P_total"] = s["P_sp_ca"] + s["P_mu"]

# vim: ts=4:sw=4:et
