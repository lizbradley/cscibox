"""
PDPaleomag.py

Copyright (c) 2006-2007 University of Colorado. All rights reserved.

Do not change the paleomagnetic intensity from that of it's
present day value

"""

from ACE.Framework.Component import Component

class PDPaleomag(Component):
    def __init__(self, collections, workflow):
        super(PDPaleomag, self).__init__(collections, workflow)
        self.values = collections.get("paleomag")
        self.keys   = self.values.keys()
        self.keys.sort()
        self.present_day = None

    def __call__(self, samples):
        for s in samples:
            s["paleomagnetic intensity"] = self.getInterpolatedIntensity(0.0)

        return (([self.get_connection()], samples),)

    def getInterpolatedIntensity(self, age):
        if self.present_day != None:
            return self.present_day

        A = self.keys[0]
        B = self.keys[1]

        # calculate A_int + (age - A) * ((B_int - A_int)/(B -A))
        A_int = self.values[A]
        B_int = self.values[B]

        int_diff  = B_int - A_int
        age_diff  = B - A
        targ_diff = age - A

        div     = int_diff / age_diff
        product = targ_diff * div

        self.present_day = A_int + product
        return self.present_day

# vim: ts=4:sw=4:et
