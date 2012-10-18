"""
StepForCalibration.py

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
from ACE.GUI.Events.ProgressEvents import EVT_UPDATE_TIME
from ACE.GUI.Events.ProgressEvents import EVT_UPDATE_PROGRESS

class StepForCalibration(Component):

    def __init__(self, collections, workflow):
        super(StepForCalibration, self).__init__(collections, workflow)
        self.iterations = {}
        self.count      = 0
        self.constants = collections.get("Constants")

    def __call__(self, samples):
        false = []
        true = []
        
        maxage = 0
        
        for s in samples:
            s_id      = s["id"]

            if self.iterations.has_key(s_id):
                iters = self.iterations[s_id]
                if iters > 150000:
                    self.count += 1

                    print "(" + str(self.count) + "/" + str(self.workflow.total_samples) + ": Giving up on Sample <" + s_id + "> on iteration " + str(self.iterations[s_id])
                    
                    evt = UpdateProgressEvent(numCompleted = self.count)
                    wx.PostEvent(self.workflow.dialog, evt)
                    
                    true.append(s)
                    del self.iterations[s_id]
                    continue
                self.iterations[s_id] = iters + 1
            else:
                self.iterations[s_id] = 0

            age             = s["age"]
            independent_age = s["independent age"]

            if abs(independent_age - age) < self.experiment["timestep"]:
                self.count += 1
                print "(" + str(self.count) + "/" + str(self.workflow.total_samples) + ": Finished processing Sample <" + s_id + "> on iteration " + str(self.iterations[s_id])
                
                evt = UpdateProgressEvent(numCompleted = self.count)
                wx.PostEvent(self.workflow.dialog, evt)
                
                true.append(s)
                del self.iterations[s_id]
            else:
                s["age"] += self.experiment["timestep"]
                if s["age"] > maxage:
                    maxage = s["age"]
                false.append(s)

        # print "current age: %d" % (maxage)
        evt = UpdateTimeEvent(time = maxage)
        wx.PostEvent(self.workflow.dialog, evt)

        time.sleep(0.001)

        return (([self.get_connection()], true),
                ([self.get_connection("loop")], false))

# vim: ts=4:sw=4:et
