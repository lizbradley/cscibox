"""
InitCalibration.py

Copyright (c) 2006-2007 University of Colorado. All rights reserved.
"""

from ACE.Framework.Component import Component

class InitCalibration(Component):

    def __call__(self, samples):
        valid = []
        for s in samples:
            s["age"] = 0.0
            # only allow samples with an independent age attribute
            # to go through the loop
            if s.has_key("independent age"):
                valid.append(s)

        return (([self.get_connection()], valid),)

# vim: ts=4:sw=4:et
