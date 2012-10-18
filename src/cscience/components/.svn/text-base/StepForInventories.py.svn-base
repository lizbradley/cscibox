"""
StepForInventories.py

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

import time

import wx

from ACE.Framework.Component import Component

from ACE.GUI.Events.ProgressEvents import UpdateTimeEvent
from ACE.GUI.Events.ProgressEvents import UpdateProgressEvent
from ACE.GUI.Events.ProgressEvents import UpdateTotalRange

class StepForInventories(Component):

    def __init__(self, collections, workflow):
        super(StepForInventories, self).__init__(collections, workflow)
        self.iterations = {}
        self.inventory  = {}
        self.count      = 0
        self.constants  = collections.get("Constants")
        self.first_iter = True

    def __call__(self, samples):
        false = []
        true = []

        maxage = 0
        
        # print "In StepForInventories"
        # print self.iterations.keys()
        # print self.inventory.keys()
        # print len(samples)
        
        for s in samples:
            s_id = s["id"]

            # print "processing %s" % (s_id)
            
            if self.iterations.has_key(s_id):
                iters = self.iterations[s_id]
                # print "iters for %s = %d" % (s_id, self.iterations[s_id])
                if iters > 150000:
                    self.count += 1
                    print "(" + str(self.count) + "/" + str(self.workflow.total_samples) + ": Giving up on Sample <" + s_id + "> on iteration " + str(self.iterations[s_id])
                    
                    self.workflow.browser.saturated.append(s_id)
                    
                    evt = UpdateProgressEvent(numCompleted = self.count)
                    wx.PostEvent(self.workflow.dialog, evt)
                    
                    true.append(s)
                    del self.iterations[s_id]
                    continue
                    
                current_inv  = s["Inv_c_mod"]
                previous_inv = self.inventory[s_id]
                
                # print "current inv for %s: %d" % (s_id, current_inv)
                # print "previous inv for %s: %d" % (s_id, previous_inv)
                # print "difference: %d" % (int(previous_inv - current_inv))
                
                if (int(previous_inv - current_inv) == 0) and (current_inv > 0) and (iters > 10):
                    self.count += 1

                    print "(" + str(self.count) + "/" + str(self.workflow.total_samples) + ": Giving up on Sample <" + s_id + "> on iteration " + str(self.iterations[s_id])

                    self.workflow.browser.saturated.append(s_id)

                    evt = UpdateProgressEvent(numCompleted = self.count)
                    wx.PostEvent(self.workflow.dialog, evt)
                    
                    true.append(s)
                    del self.iterations[s_id]
                    continue
                    
                self.inventory[s_id] = current_inv
                self.iterations[s_id] = iters + 1
            else:
                self.iterations[s_id] = 0
                self.inventory[s_id]  = s["Inv_c_mod"]
                

            if s["Inv_c_mod"] <= 0:
                self.count += 1
                print "(" + str(self.count) + "/" + str(self.workflow.total_samples) + ": Finished processing Sample <" + str(s_id) + "> on iteration " + str(self.iterations[s_id])
                
                evt = UpdateProgressEvent(numCompleted = self.count)
                wx.PostEvent(self.workflow.dialog, evt)
                
                true.append(s)
                del self.iterations[s_id]
            else:
                s["age"] += self.experiment["timestep"]
                if s["age"] > maxage:
                    maxage = s["age"]
                false.append(s)
                
        if self.first_iter:
            if samples[0]['Inv_c_mod'] != 1000000:
            
                max_sample   = max(samples, key=lambda x: x['Inv_c_mod'])
                self.max_inv = max_sample['Inv_c_mod']
            
                evt = UpdateTotalRange(max_value = int(self.max_inv))
                wx.PostEvent(self.workflow.dialog, evt)
            
                self.first_iter = False
        else:
            current_max_sample = max(samples, key=lambda x: x['Inv_c_mod'])
            current_inv = current_max_sample['Inv_c_mod']
            
            # print "self.max_inv = %d" % (self.max_inv)
            # print "current_inv = %d" % (current_inv)
            
            evt = UpdateTimeEvent(time = maxage, progress=int(self.max_inv - current_inv))
            wx.PostEvent(self.workflow.dialog, evt)

        time.sleep(0.001)

        return (([self.get_connection()], true),
                ([self.get_connection("loop")], false))

# vim: ts=4:sw=4:et
