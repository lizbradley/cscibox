"""
TopographyFactor45.py

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

# Calculator GUI:

# So that 8/3 will be 2.6666 and not 2
from __future__ import division
import wx
import math
import numpy
import wx.lib.hyperlink as hl
from wx.lib.fancytext import StaticFancyText

class Calculator(wx.Dialog):
   '''Main calculator dialog'''
   def __init__(self):

       wx.Dialog.__init__(self, None, -1, "45 Degree Topographic Shielding") 
       sizer = wx.BoxSizer(wx.VERTICAL) # Main vertical sizer

       #label = wx.StaticText(self, -1, "Topographic Shielding")
       #sizer.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
       
       # Compass Boxes in analog clock like formation
       box = wx.GridBagSizer(1,1) # Current calculation
       self.sample = wx.StaticText(self, -1, "Sample Site")
       box.Add(self.sample, (2,2), (1,1) , wx.ALIGN_CENTRE|wx.ALL, 5)
       self.N = wx.TextCtrl(self, -1, "0", name="test", size=(40,-1))
       box.Add(self.N, (0,2), (1,1), wx.ALIGN_CENTRE|wx.ALL, 5)
       self.NW = wx.TextCtrl(self, -1, "0", size=(40,-1))
       box.Add(self.NW, (1,1), (1,1), wx.ALIGN_CENTRE|wx.ALL, 5)
       self.W = wx.TextCtrl(self, -1, "0", size=(40,-1))
       box.Add(self.W, (2,0), (1,1), wx.ALIGN_CENTRE|wx.ALL, 5)
       self.SW = wx.TextCtrl(self, -1, "0", size=(40,-1))
       box.Add(self.SW, (3,1), (1,1), wx.ALIGN_CENTRE|wx.ALL, 5)
       self.S = wx.TextCtrl(self, -1, "0", size=(40,-1))
       box.Add(self.S, (4,2), (1,1), wx.ALIGN_CENTRE|wx.ALL, 5)
       self.SE = wx.TextCtrl(self, -1, "0", size=(40,-1))
       box.Add(self.SE, (3,3), (1,1), wx.ALIGN_CENTRE|wx.ALL, 5)
       self.E = wx.TextCtrl(self, -1, "0", size=(40,-1))
       box.Add(self.E, (2,5), (1,1), wx.ALIGN_CENTRE|wx.ALL, 5)
       self.NE = wx.TextCtrl(self, -1, "0", size=(40,-1))
       box.Add(self.NE, (1,3), (1,1), wx.ALIGN_CENTRE|wx.ALL, 5)
       sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 0)
       
       # Dip Box
       box = wx.BoxSizer(wx.HORIZONTAL) # Current calculation

       label = StaticFancyText(self, -1, "Sample Dip (<sup>o</sup>)")
       box.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)

       self.dip = wx.TextCtrl(self, -1, "0", size=(40,-1))
       box.Add(self.dip, 1, wx.ALIGN_CENTRE|wx.ALL, 5)

       sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

       # Strike Box
       box = wx.BoxSizer(wx.HORIZONTAL) # Current calculation

       label = StaticFancyText(self, -1, "Sample Strike (<sup>o</sup>)")
       box.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)

       self.strike = wx.TextCtrl(self, -1, "0", size=(40,-1))
       box.Add(self.strike, 1, wx.ALIGN_CENTRE|wx.ALL, 5)

       sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

       # m Box
       box = wx.BoxSizer(wx.HORIZONTAL) # Current calculation

       label = wx.StaticText(self, -1, "m")
       box.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)

       self.m = wx.TextCtrl(self, -1, "2.3", size=(40,-1))
       box.Add(self.m, 1, wx.ALIGN_CENTRE|wx.ALL, 5)

       sizer.Add(box, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

       # [ Calculate Topography Factor Button Here ]
       c = wx.Button(self, -1, "Calculate Topographic Shielding")
       self.Bind(wx.EVT_BUTTON, self.OnButton, c)
       sizer.Add(c, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
       self.equal = c
       
       # Answer box here
       self.display = wx.ComboBox(self, -1) # Current calculation
       sizer.Add(self.display, 0, wx.EXPAND) # Add to main sizer

       # Line
       line = wx.StaticLine(self, -1, size=(20,-1), style=wx.LI_HORIZONTAL)
       sizer.Add(line, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.TOP, 5)

        # Default Web links:
       box = wx.BoxSizer(wx.HORIZONTAL) # Current calculation
       self._hyper1 = hl.HyperLinkCtrl(self, wx.ID_ANY, "Online Help",
                                       URL="http://ace.hwr.arizona.edu/?page_id=21")
       box.Add(self._hyper1, 0, wx.ALIGN_CENTER_VERTICAL, 0)

       btnsizer = wx.StdDialogButtonSizer()
       box.Add(btnsizer, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)

       btn = wx.Button(self, wx.ID_OK,'Close')
       btnsizer.AddButton(btn)
       btnsizer.Realize()

       sizer.Add(box, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

       self.SetSizer(sizer)
       sizer.Fit(self)

   def OnButton(self, evt):
       '''Handle button click event'''
       # Get title of clicked button
       label = evt.GetEventObject().GetLabel()

       if label == "Calculate Topographic Shielding": # Calculate
           try:
               def getInterpolatedInclinations(ang):

                      A = None
                      B = None
                      i = 0

                      while i < (len(angls) - 1):
                          A = angls[i]
                          B = angls[i+1]

                          if ((A <= ang) and (ang < B)):
                               break

                          i = i + 1

                      A_int = elevs[i]
                      B_int = elevs[i+1]

                      int_diff = B_int - A_int
                      ang_diff = B - A
                      targ_diff = ang - A

                      div = int_diff / ang_diff
                      product = targ_diff * div

                      return A_int + product

               elevs = [float(self.N.GetValue()), float(self.NE.GetValue()), 
                        float(self.E.GetValue()), float(self.SE.GetValue()),
                        float(self.S.GetValue()), float(self.SW.GetValue()),
                        float(self.W.GetValue()), float(self.NW.GetValue()),
                        float(self.N.GetValue())]
               angls = [0, 45, 90, 135, 180, 225, 270, 315, 360]
               PI = math.pi
               dipRadians = float(self.dip.GetValue()) * PI / 180.0
               strikeRadians = float(self.strike.GetValue()) * PI / 180
               m = float(self.m.GetValue())

               step = 1 # Angular integration step size (degrees)
               sum = 0

               for ang in range(0,360-step,step):
                  inc = (getInterpolatedInclinations(ang)) * PI / 180.0
                  sampleAngl = ang * PI / 180.0 - (strikeRadians - PI / 2)
                  #How does the sample see this angle?
                  sampleInc = max(inc,math.atan(math.tan(dipRadians) * math.cos(sampleAngl)))
                  #How does the sample see this inclination?
                  costerm = math.cos(PI / 2 - sampleInc);
                  # PI / 2 because we want angle from directly above, not horizon
                  cospow = costerm**(m+1)
                  sum = sum + cospow * step * PI / 180.0

               sum = sum / (2 * PI)
               compute = 1 - sum

                # Ignore empty calculation
               #if not compute.strip():
               if not compute:
                   return

               # Calculate result
               # result = eval(compute)

               # Add to history
               self.display.Insert(str(compute), 0)
              
               # Show result
               #self.display.SetValue(str(result))
               self.display.SetValue(str(compute))
           except Exception, e:
               wx.LogError(str(e))
               return

       else: # Just add button text to current calculation
           self.display.SetValue(self.display.GetValue() + label)
           self.equal.SetFocus() # Set the [=] button in focus

if __name__ == "__main__":
   # Run the application
   app = wx.PySimpleApp()
   dlg = Calculator()
   dlg.ShowModal()
   dlg.Destroy()
