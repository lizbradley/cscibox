"""
InstPaleomag.py

Copyright (c) 2006-2007 University of Colorado. All rights reserved.
"""

from ACE.Framework.Component import Component

class InstPaleomag(Component):
    def __init__(self, collections, workflow):
        super(InstPaleomag, self).__init__(collections, workflow)
        self.values = collections.get("paleomag")
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
