"""
StepForInventories.py

Copyright (c) 2006-2007 University of Colorado. All rights reserved.
"""

from ACE.Framework.Component import Component

class StepForInventories(Component):

    def __init__(self, collections, workflow):
        super(StepForInventories, self).__init__(collections, workflow)
        self.iterations = {}
        self.count      = 0
        self.constants = collections.get("constants")

    def __call__(self, samples):
        false = []
        true = []

        for s in samples:
            s_id = s["id"]

            if self.iterations.has_key(s_id):
                iters = self.iterations[s_id]
                if iters > 150000:
                    self.count += 1
                    print "(" + str(self.count) + "/" + str(self.workflow.total_samples) + ": Giving up on Sample <" + s_id + "> on iteration " + str(self.iterations[s_id])
                    true.append(s)
                    del self.iterations[s_id]
                    continue
                self.iterations[s_id] = iters + 1
            else:
                self.iterations[s_id] = 0

            if s["Inv_c_mod"] <= 0:
                self.count += 1
                print "(" + str(self.count) + "/" + str(self.workflow.total_samples) + ": Finished processing Sample <" + str(s_id) + "> on iteration " + str(self.iterations[s_id])
                true.append(s)
                del self.iterations[s_id]
            else:
                s["age"] += self.experiment["timestep"]
                false.append(s)

        return (([self.get_connection()], true),
                ([self.get_connection("loop")], false))

# vim: ts=4:sw=4:et
