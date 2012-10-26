"""
Lifton2008CutoffRigidity.py

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

Lifton doi : 10.1016/j.epsl..01.021
"""

from ACE.Framework.Component import Component
import math
from scipy import interp

class Lifton2008CutoffRigidity(Component):
    def __init__(self, collections, workflow):
        super(Lifton2008CutoffRigidity, self).__init__(collections, workflow)

        self.values    = collections.get("Cutoff Rigidity - Korte Constable 2005")

        self.a1  = -2.4104      # Table 1 Lifton  2008
        self.a2  = -9.6328E-2
        self.a3  = 1.6943E-1
        self.a4  = -9.7615E-1
        self.a5  = 2.2676E-2
        self.a6  = 2.5525
        self.a7  = 31.568
        self.a8  = -2.2159E-2
        self.a9  = -1.4561E-1
        self.a10 = -7.3513E-1
        self.a11 = -14.145
        self.a12 = -2.7544E-4

    def __call__(self, samples):
        PI = math.pi
        for s in samples:

            age = float(s["age"])
            if age <= 6900: #Use continuous record

              #Nearest neighbour spatial interpolation
              lat5 = 5 * round(s["latitude"]/5.0)
              lon5 = 15 * round(s["longitude"]/15.0)

              #Linear temporal evaluation
              ageYoung = 500 * math.floor(age/500.0)
              ageOld = 500 * math.ceil(age/500.0)
              if ageOld == 7000:
                ageOld = 6900
              rigidityYoung=self.values[ageYoung,lon5,lat5]
              rigidityOld=self.values[ageOld,lon5,lat5]

              rigidityNow = interp(age,[ageYoung, ageOld],[rigidityYoung, rigidityOld], right=None)
              if age == ageOld:
                rigidityNow = self.values[ageOld,lon5,lat5] 
              s["rigidity"] = rigidityNow

              SouthPoleRigidityNow = self.values[0,0,-90]
       
            else: #Use > 7 ka estimate (Equation 4) 
              arg1 = s["paleomagnetic latitude"] * PI / 180.0  
              arg2 = self.a2 / s["paleomagnetic intensity"]
              cosLat = math.cos(arg1 + arg2)
              val1 = self.a1 * abs(cosLat)

              arg2 = self.a4 / s["paleomagnetic intensity"]
              cosLat = math.cos(arg1 + arg2)
              val2 = self.a3 * abs(cosLat)**2.0

              arg2 = self.a6 / s["paleomagnetic intensity"]
              cosLat = math.cos(arg1 + arg2)
              val3 = self.a5 * abs(cosLat)**3.0

              arg2 = self.a8 / s["paleomagnetic intensity"]
              cosLat = math.cos(arg1 + arg2)
              val4 = self.a7 * abs(cosLat)**4.0

              arg2 = self.a10 / s["paleomagnetic intensity"]
              cosLat = math.cos(arg1 + arg2)
              val5 = self.a9 * abs(cosLat)**5.0
            
              arg2 = self.a12 / s["paleomagnetic intensity"]
              cosLat = math.cos(arg1 + arg2)
              val6 = self.a11 * abs(cosLat)**6.0
            
              s["rigidity"] = s["paleomagnetic intensity"] * (val1 + val2 + val3 + val4 + val5 + val6)

              #Check for latitude higher than 60 degrees
              if s["rigidity"] < 1:
                s["rigidity"] = 1.0

        return (([self.get_connection()], samples),)

# vim: ts=4:sw=4:et
