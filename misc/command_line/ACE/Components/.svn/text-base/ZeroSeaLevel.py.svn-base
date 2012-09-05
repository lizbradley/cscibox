"""
ZeroSeaLevel.py

Copyright (c) 2006-2007 University of Colorado. All rights reserved.

This class is the base class of InstSeaLevel.py. That class calculates
eustatic sea level changes as a function of time.  This is then used
to calulate elevation changes wrt sea level and pressure changes as 
a function of time.  However Osmaston 2006 
(doi 10.1016/j.yqres.2005.11.004) does not think that sea level changes
should be used to calulate past changes in climate. So, in this
component, we set eustatic sea-level change to zero.
"""

from ACE.Framework.Component import Component

import math

class ZeroSeaLevel(Component):
    def __init__(self, collections, workflow):
        super(ZeroSeaLevel, self).__init__(collections, workflow)
        self.constants = collections.get("constants")
        self.values    = collections.get("fairbanks")

    def __call__(self, samples):
        for s in samples:
            self.set_pressure(s)
            self.set_temperature(s)
            self.set_lapse_rate(s)

            s["eustatic sea-level change"] = 0.0
            # For all times, return a value of sea level change of zero.

        return (([self.get_connection()], samples),)

    def set_lapse_rate(self, s):
        if not s.has_key("calculated lapse rate"):
            result = None
            if s.has_key("default lapse rate"):
                rate = s["default lapse rate"]
                result = rate / 1000.0
            else:
                result = self.constants["beta_0"]
            s["calculated lapse rate"] = result

    def set_pressure(self, s):
        if not s.has_key("sea level pressure"):
            result = None
            if s.has_key("default sea level pressure"):
                pressure = s["default sea level pressure"]
                result = pressure / 1.01959
            else:
                result = self.constants["p_0"]
            s["sea level pressure"] = result

    def set_temperature(self, s):
        if not s.has_key("sea level temperature"):
            result = None
            if s.has_key("default sea level temperature"):
                result = s["default sea level temperature"] + 273.16
            else:
                result = self.constants["T_0"]
            s["sea level temperature"] = result

# vim: ts=4:sw=4:et
