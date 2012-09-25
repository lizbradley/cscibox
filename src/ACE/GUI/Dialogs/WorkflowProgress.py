"""
WorkflowProgress.py

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

import wx

from ACE.GUI.Events.ProgressEvents import EVT_UPDATE_TIME
from ACE.GUI.Events.ProgressEvents import EVT_UPDATE_PROGRESS
from ACE.GUI.Events.ProgressEvents import EVT_UPDATE_RANGE
from ACE.GUI.Events.ProgressEvents import EVT_UPDATE_SAMPLES

class WorkflowProgress(wx.Frame):
    def __init__(self, parent, title, numSamples, maxAge):
        wx.Frame.__init__(self, parent, -1, title)
        
        self.bar = wx.Gauge(self, wx.ID_ANY, range=maxAge)
        self.progress = wx.StaticText(self, wx.ID_ANY, "%4d of %4d Samples Processed" % (0, numSamples))
        self.time = wx.StaticText(self, wx.ID_ANY, "Time Step: 0")
        self.numSamples = numSamples
        self.button = wx.Button(self, wx.ID_ANY, "Cancel")
        self.cancel = False
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.bar, border=5, flag=wx.ALL | wx.EXPAND)
        sizer.Add(self.progress, border=5, flag=wx.ALIGN_LEFT | wx.ALL)
        sizer.Add(self.time, border=5, flag=wx.ALIGN_LEFT | wx.ALL)
        sizer.Add(self.button, border=5, flag=wx.ALIGN_CENTER | wx.ALL)
        
        self.SetSizer(sizer)
        sizer.Fit(self)
        
        self.Centre()
        
        self.MakeModal(True)

        self.Bind(EVT_UPDATE_TIME, self.set_time)
        self.Bind(EVT_UPDATE_PROGRESS, self.set_progress)
        self.Bind(EVT_UPDATE_RANGE, self.set_range)
        self.Bind(EVT_UPDATE_SAMPLES, self.set_total_samples)
        self.Bind(wx.EVT_BUTTON, self.OnCancel, self.button)

    def set_time(self, evt):
        if hasattr(evt, "progress"):
            # print "Setting Current value to %d" % (evt.progress)
            self.bar.SetValue(evt.progress)
        else:
            # print "Setting Current value to %d" % (evt.time)
            self.bar.SetValue(evt.time)
        self.time.SetLabel("Time Step: %d" % evt.time)
        self.Layout()
    
    def set_progress(self, evt):
        self.progress.SetLabel("%4d of %4d Samples Processed" % (evt.numCompleted, self.numSamples))
        if evt.numCompleted == self.numSamples:
            self.MakeModal(False)
            wx.FutureCall(2000, self.Close)
        self.Layout()
        
    def set_range(self, evt):
        self.bar.SetRange(evt.max_value)
        # print "Setting Max value to %d" % (evt.max_value)
        self.Layout()
        
    def set_total_samples(self, evt):
        self.numSamples = evt.num_samples
        self.progress.SetLabel("%4d of %4d Samples Processed" % (0, evt.num_samples))
        self.Layout()
        
    def OnCancel(self, event):
        self.cancel = True
        self.MakeModal(False)
        wx.FutureCall(1000, self.Close)
        
        
