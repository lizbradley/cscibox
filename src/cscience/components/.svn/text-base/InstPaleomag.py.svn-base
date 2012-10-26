"""
InstPaleomag.py

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

class InstPaleomag(Component):
    def __init__(self, collections, workflow):
        super(InstPaleomag, self).__init__(collections, workflow)
        self.values = collections.get("Geomagnetic Intensity - Guyodo Valet 1999")
        self.keys   = self.values.keys()
        self.keys.sort()
        self.mean   = None

    def __call__(self, samples):
        for s in samples:
            s["paleomagnetic intensity"] = self.getInterpolatedIntensity(s["age"])

        return (([self.get_connection()], samples),)

    def getMeanIntensity(self):
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

    def getInterpolatedIntensity(self, age):

        if self.values.has_key(age):
            return self.values[age]

        # check to see if we have an age past the end of the data collection
        if age > self.keys[len(self.keys)-1]:
            return self.getMeanIntensity();

        A    = None
        B    = None
        i    = 0

        while i < (len(self.keys) - 1):
            A = self.keys[i]
            B = self.keys[i+1]

            if ((A < age) and (age < B)):
                break

            i = i + 1

        # calculate A_int + (age - A) * ((B_int - A_int)/(B -A))
        A_int = self.values[A]
        B_int = self.values[B]

        int_diff  = B_int - A_int
        age_diff  = B - A
        targ_diff = age - A

        div     = int_diff / age_diff
        product = targ_diff * div

        return A_int + product

# vim: ts=4:sw=4:et
