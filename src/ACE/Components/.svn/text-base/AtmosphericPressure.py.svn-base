"""
AtmosphericPressure.py

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
"""

from ACE.Framework.Component import Component

class AtmosphericPressure(Component):
    def __init__(self, collections, workflow):
        super(AtmosphericPressure, self).__init__(collections, workflow)
        self.constants = collections.get("Constants")

    def __call__(self, samples):
        for s in samples:
            pressure    = s["sea level pressure"] * 1.01959
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
