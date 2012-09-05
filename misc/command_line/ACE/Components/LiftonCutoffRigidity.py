"""
LiftonCutoffRigidity.py

Copyright (c) 2006-2007 University of Colorado. All rights reserved.

Lifton doi : 10.1016/j.epsl.2005.07.001
"""

from ACE.Framework.Component import Component
import math

class LiftonCutoffRigidity(Component):
    def __init__(self, collections, workflow):
        super(LiftonCutoffRigidity, self).__init__(collections, workflow)

        self.d1 = 15.765		# Equation 1 Lifton 2005
        self.d2 = 3.800			# Equation 2 Lifton 2005

    def __call__(self, samples):
        PI = math.pi
        for s in samples:

            #Calculate cutoff rigidity
            cosLat = math.cos(s["paleomagnetic latitude"] * PI / 180.0)
            cosPow = cosLat**self.d2

            s["rigidity"] = self.d1 * s["paleomagnetic intensity"] * cosPow

            #Check for latitude higher than 55 degrees
            cos55Lat = math.cos(55.0 * PI / 180.0)
            cos55pow = cos55Lat**self.d2
            
            if s["rigidity"] < self.d1 * cos55pow:
                s["rigidity"] = self.d1 * cos55pow

        return (([self.get_connection()], samples),)

# vim: ts=4:sw=4:et
