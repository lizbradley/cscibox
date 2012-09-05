"""
LiftonCutoffRigidity.py

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
