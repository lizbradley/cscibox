"""
OutputForNuclideAges.py

Copyright (c) 2006-2007 University of Colorado. All rights reserved.
"""

from ACE.Framework.Component import Component

import math

class OutputForNuclideAges(Component):
    
    def __call__(self, samples):

        self.timestep = self.experiment["timestep"]

        for s in samples:
            self.calculateInv_m(s);
            self.calculateInvmUncertainty(s);
            self.calculateAgeUncertainty(s);

        return (([self.get_connection()], samples),)

    def calculateInv_m(self, s):
        s["measured inventory"] = s["cosmogenic inventory"]

    def calculateInvmUncertainty(self, s):
        s["measured inventory uncertainty"] = s["cosmogenic inventory uncertainty"]

    def calculateAgeUncertainty(self, s):
        # calculate age*measured inventory uncertainty/Inv_c
        s["age uncertainty"] = (s["age"] * s["cosmogenic inventory uncertainty"]) / s["cosmogenic inventory"]
        # round to nearest timestep
        s["age uncertainty"] = round (s["age uncertainty"] / self.timestep) * self.timestep


# vim: ts=4:sw=4:et
