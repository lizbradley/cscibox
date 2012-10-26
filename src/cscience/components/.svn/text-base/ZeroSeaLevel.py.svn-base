"""
ZeroSeaLevel.py

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
        self.constants = collections.get("Constants")
        self.values    = collections.get("Sea Level - Fairbanks 1989 Shackleton 2000")

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
            if s.has_key("default sea-level pressure"):
                pressure = s["default sea-level pressure"]
                result = pressure / 1.01959
            else:
                result = self.constants["p_0"]
            s["sea level pressure"] = result

    def set_temperature(self, s):
        if not s.has_key("sea level temperature"):
            result = None
            if s.has_key("default sea-level temperature"):
                result = s["default sea-level temperature"] + 273.16
            else:
                result = self.constants["T_0"]
            s["sea level temperature"] = result

# vim: ts=4:sw=4:et
