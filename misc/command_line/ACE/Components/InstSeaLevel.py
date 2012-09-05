"""
InstSeaLevel.py

Copyright (c) 2006-2007 University of Colorado. All rights reserved.
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
