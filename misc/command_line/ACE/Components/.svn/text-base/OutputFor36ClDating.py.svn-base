"""
OutputFor36ClDating.py

Copyright (c) 2006-2007 University of Colorado. All rights reserved.
"""

from ACE.Components.OutputFor36ClAges  import OutputFor36ClAges

import math

class OutputFor36ClDating(OutputFor36ClAges):
    
    def __init__(self, collections, workflow):
        super(OutputFor36ClDating, self).__init__(collections, workflow)

    def __call__(self, samples):
        super(OutputFor36ClDating, self).__call__(samples)

        return (([None], []),)

    def calculateInvcUncertainty(self, s):
        # calculate =SQRT(measured inventory uncertainty^2+(0.2*Inv_r)^2)
        prod1 = 0.2 * s["nucleogenic inventory"]
        term1 = s["measured inventory uncertainty"]**2.0
        term2 = prod1**2.0
        term3 = s["Inv_c_uncertainty"]**2.0
        # Do not include production rate uncertainty
        #sum1  = term1 + term2 + term3
        sum1  = term1 + term2
        s["cosmogenic inventory uncertainty"] = math.sqrt(sum1)

# vim: ts=4:sw=4:et
