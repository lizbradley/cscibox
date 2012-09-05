"""
OutputForNuclideDating.py

Copyright (c) 2006-2007 University of Colorado. All rights reserved.
"""

from ACE.Components.OutputForNuclideAges  import OutputForNuclideAges

import math

class OutputForNuclideDating(OutputForNuclideAges):
    
    def __init__(self, collections, workflow):
        super(OutputForNuclideDating, self).__init__(collections, workflow)

    def __call__(self, samples):

        self.timestep = self.experiment["timestep"]

        super(OutputForNuclideDating, self).__call__(samples)

        return (([None], []),)

    def calculateInvmUncertainty(self, s):
        super(OutputForNuclideDating, self).calculateInvmUncertainty(s)
        sum1 = s["cosmogenic inventory uncertainty"]**2.0 + s["Inv_c_uncertainty"]**2.0
        #Use analytical error, not production rate error
        #s["Inv_err"] = sum
        s["Inv_err"] = s["cosmogenic inventory uncertainty"]

    def calculateAgeUncertainty(self, s):
        # calculate age*measured inventory uncertainty/Inv_c
        s["age uncertainty"] = (s["age"] * s["Inv_err"]) / s["cosmogenic inventory"]
        # round to nearest timestep
        s["age uncertainty"] = round (s["age uncertainty"] / self.timestep) * self.timestep

# vim: ts=4:sw=4:et
