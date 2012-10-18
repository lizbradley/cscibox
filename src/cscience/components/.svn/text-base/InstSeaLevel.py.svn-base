"""
InstSeaLevel.py

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

from ACE.Components.ZeroSeaLevel import ZeroSeaLevel

import math

class InstSeaLevel(ZeroSeaLevel):
    def __init__(self, collections, workflow):
        super(InstSeaLevel, self).__init__(collections, workflow)
        self.keys      = self.values.keys()
        self.keys.sort()
        self.mean   = None

    def __call__(self, samples):
        for s in samples:
            self.set_pressure(s)
            self.set_temperature(s)
            self.set_lapse_rate(s)

            s["eustatic sea-level change"] = self.get_avg_sea_level_change(s)

        return (([self.get_connection()], samples),)

    def get_avg_sea_level_change(self, s):
        age = s["age"]

        div1 = float(age) / 1000.0

        index2 = math.ceil(div1)

        index1 = index2 - 1.0

        avg1 = self.get_sea_level(index1)
        avg2 = self.get_sea_level(index2)

        diff1 = avg2 - avg1
        diff2 = index2 - index1

        div2 = diff1 / diff2

        product = div2 * (div1 - index1)

        return avg1 + product

    def get_sea_level(self, age):
        if age > self.keys[len(self.keys)-1]:
            return self.get_mean_sea_level();
        return self.values[age]

    def get_mean_sea_level(self):
        if self.mean != None:
            return self.mean;

        numKeys = len(self.keys)
        total   = 0.0
        i       = 0

        while i < len(self.keys):
            total += self.values[self.keys[i]]
            i += 1

        self.mean = total / float(numKeys)
        return self.mean

# vim: ts=4:sw=4:et
