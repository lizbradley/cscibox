"""
InventoryChangeCalculation.py

Copyright (c) 2006-2007 University of Colorado. All rights reserved.
"""

from ACE.Framework.Component import Component

import math

class InventoryChangeCalculation(Component):
    def __init__(self, collections, workflow):
        super(InventoryChangeCalculation, self).__init__(collections, workflow)
        self.constants = collections.get("constants")
        self.LAMBDA_36 = self.constants["lambda_36"]
        

    def __call__(self, samples):
        for s in samples:
            if s["age"] == self.experiment["timestep"]:
                # first time step. Set the 'modelled' inventory Inv_c_mod
                s["Inv_c_mod"] = (s["ClCalc"] * s["clRatio"] * 0.000000000000001) - s["nucleogenic inventory"]
                s["Inv_c_uncertainty"] = 0.0
            else:
                self.calculate_age(s)

        return (([self.get_connection()], samples),)

    def calculate_age(self, s):
        # calculate how much the inventory has changed over the timestep
        # also wind the age back timestep (10) years
        prod0 = -1.0 * self.LAMBDA_36 * self.experiment["timestep"]
        minu1 = 1.0 - math.exp(prod0)
        term1 = minu1 / self.LAMBDA_36
        prod1 = s["P_total"] * term1
        #prod1 = s["P_total"] * self.experiment["timestep"]
        prod2 = -1.0 * self.LAMBDA_36 * s["age"]
        prod3 = math.exp(prod2)
        prod4 = prod3 * prod1
        s["Inv_c_mod"] -= prod4
        prod5 = s["P_total_uncertainty"] * term1
        #prod5 = s["P_total_uncertainty"] * self.experiment["timestep"]
        prod6 = prod3 * prod5
        s["Inv_c_uncertainty"] += prod6

# vim: ts=4:sw=4:et
