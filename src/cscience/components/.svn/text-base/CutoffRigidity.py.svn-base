"""
CutoffRigidity.py

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

class CutoffRigidity(Component):
    def __init__(self, collections, workflow):
        super(CutoffRigidity,self).__init__(collections, workflow)

        self.Rc_power = [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0]

        self.Rc_d = [-0.00430765994196207,
                 0.0243522167282964,
                -0.00467574894468803,
                 0.00033287122617234,
                -0.0000109931229314564,
                 0.000000170370253903044,
                -0.00000000100429401966186]

        self.Rc_e = [14.7924688273843,
                -0.06679890088318,
                 0.00357143630519525,
                 0.0000280054246280052,
                -0.0000239018299798327,
                 0.000000661788482591492,
                -0.00000000502826180115525]

    def __call__(self, samples):
        for s in samples:
            if s["paleomagnetic latitude"] < 55:

                Array_1 = []
                Array_2 = []
                Array_3 = []
                for i in range(7):
                    product = self.Rc_e[i] * s["paleomagnetic intensity"]
                    Array_1.append(product + self.Rc_d[i])

                if s["paleomagnetic latitude"] != 0:

                    for i in range(7):
                        Array_2.append(s["paleomagnetic latitude"]**self.Rc_power[i])
                else:

                    lat = s["paleomagnetic latitude"] + 0.001;

                    for i in range(7):
                        Array_2.append(lat**self.Rc_power[i])

                for i in range(7):
                    Array_3.append(Array_1[i] * Array_2[i])

                total = 0.0

                for i in range(7):
                    total += Array_3[i]

                s["rigidity"] = total
            else:
                s["rigidity"] = 1.0

        return (([self.get_connection()], samples),)

# vim: ts=4:sw=4:et
