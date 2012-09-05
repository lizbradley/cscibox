"""
CutoffRigidity.py

Copyright (c) 2006-2007 University of Colorado. All rights reserved.
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
