"""
InitInventories.py

Copyright (c) 2006-2007 University of Colorado. All rights reserved.
"""

from ACE.Framework.Component import Component

class InitInventories(Component):

    def __call__(self, samples):
        for s in samples:
            s["age"] = 0.0

            # if the sample doesn't have an inventory attribute
            # give it a default value
            if not s.has_key("Inv_c_mod"):
                s["Inv_c_mod"] = 1000000

        return (([self.get_connection()], samples),)

# vim: ts=4:sw=4:et
