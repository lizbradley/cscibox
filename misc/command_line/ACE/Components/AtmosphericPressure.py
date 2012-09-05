"""
AtmosphericPressure.py

Copyright (c) 2006-2007 University of Colorado. All rights reserved.
"""

from ACE.Framework.Component import Component

class AtmosphericPressure(Component):
    def __init__(self, collections, workflow):
        super(AtmosphericPressure, self).__init__(collections, workflow)
        self.constants = collections.get("constants")

    def __call__(self, samples):
        for s in samples:
            pressure    = s["sea level pressure"]
            temperature = s["sea level temperature"]
            rate        = s["calculated lapse rate"]
            elevation   = s["effective elevation"]

            g_0 = self.constants["g_0"]
            R_d = self.constants["R_d"]

            # ask Chris or Marek what this constant represents
            # then rename variable to something better!
            constant = 1.01959

            # calculate the forumula:
            # (pressure)*(1-(rate)*(elevation)/(temperature))^(g_0/(R_d*(rate)))*constant

            # calculate (g_0/(R_d*(rate)))
            prod1 = R_d * rate
            div1  = g_0 / prod1

            # calculate (1-(rate)*(elevation)/(temperature))
            prod2 = rate * elevation
            div2  = prod2 / temperature
            sub1  = 1 - div2

            # calculate sub1^div1
            # note, line below may need to be pow1 = math.pow(sub1, div1)
            pow1 = sub1**div1

            # calculate pressure * pow1 * constant
            s["atmospheric pressure"] = pressure * pow1 * constant

        return (([self.get_connection()], samples),)

# vim: ts=4:sw=4:et
