"""
InstElevation.py

Copyright (c) 2006-2007 University of Colorado. All rights reserved.
"""

from ACE.Framework.Component import Component

class InstElevation(Component):

    def __call__(self, samples):
        for s in samples:
            s["average vertical movement"] = self.get_vertical_movement(s)
            s["effective elevation"]       = self.get_effective_elevation(s)

        return (([self.get_connection()], samples),)

    def get_vertical_movement(self, s):
        rate = s["vertical movement"]

        if rate == None:
            rate = 0.0

        age = s["age"]

        return rate * age

    def get_effective_elevation(self, s):
        elevation = s["elevation"]
        rate      = s["average vertical movement"]
        change    = s["eustatic sea-level change"]

        return elevation - rate - change

# vim: ts=4:sw=4:et
