"""
GeoPolePositions.py

Copyright (c) 2006-2007 University of Colorado. All rights reserved.
"""

from ACE.Framework.Component import Component

class GeoPolePositions(Component):

    def __call__(self, samples):
        for s in samples:
            s["paleomagnetic latitude"] = abs(s["latitude"])

        return (([self.get_connection()], samples),)

# vim: ts=4:sw=4:et
