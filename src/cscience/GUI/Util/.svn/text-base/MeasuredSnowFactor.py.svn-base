"""
MeasuredSnowFactor.py

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
import wx.lib.hyperlink as hl
from wx.lib.fancytext import StaticFancyText

class Calculator(wx.Dialog):
   '''Main calculator dialog'''
   def __init__(self):

       wx.Dialog.__init__(self, None, -1, "Spallation Snow Shielding Factor") 
       sizer = wx.BoxSizer(wx.VERTICAL) # Main vertical sizer

       #label = wx.StaticText(self, -1, "Snow Shielding Factor From Mean Annual Snow Depth")
       #sizer.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)

       # Snow Thickness Box
       box = wx.BoxSizer(wx.HORIZONTAL) # Current calculation

       label = StaticFancyText(self, -1, "Mean Annual Snow Depth (cm)")
       box.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)

       self.thick = wx.TextCtrl(self, -1, "0", size=(80,-1))
       box.Add(self.thick, 1, wx.ALIGN_CENTRE|wx.ALL, 5)

       sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
       
       # Snow Attenuation Box
       box = wx.BoxSizer(wx.HORIZONTAL) # Current calculation

       label = StaticFancyText(self, -1, "Snow Attenuation (g cm<sup>-2</sup>)")
       box.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)

       self.att = wx.TextCtrl(self, -1, "160", size=(80,-1))
       box.Add(self.att, 1, wx.ALIGN_CENTRE|wx.ALL, 5)

       sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

       # Snow Density Box
       box = wx.BoxSizer(wx.HORIZONTAL) # Current calculation

       label = StaticFancyText(self, -1, "Snow Density (g cm<sup>-3</sup>)")
       box.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)

       self.dens = wx.TextCtrl(self, -1, "0.2", size=(80,-1))
       box.Add(self.dens, 1, wx.ALIGN_CENTRE|wx.ALL, 5)

       sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

       # [ Calculate Snow Factor Button Here ]
       c = wx.Button(self, -1, "Calculate Snow Factor for Spallation")
       self.Bind(wx.EVT_BUTTON, self.OnButton, c)
       sizer.Add(c, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
       self.equal = c
       
       # Answer box here
       self.display = wx.ComboBox(self, -1) # Current calculation
       sizer.Add(self.display, 0, wx.EXPAND) # Add to main sizer

       # Line
       line = wx.StaticLine(self, -1, size=(20,-1), style=wx.LI_HORIZONTAL)
       sizer.Add(line, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.TOP, 5)

       box = wx.BoxSizer(wx.HORIZONTAL) # Current calculation
       sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
       self._hyper1 = hl.HyperLinkCtrl(self, wx.ID_ANY, "Online Help",
                                       URL="http://ace.hwr.arizona.edu/?page_id=14")
       box.Add(self._hyper1, 0, wx.ALIGN_CENTER_VERTICAL, 0)
   
       btnsizer = wx.StdDialogButtonSizer()
       box.Add(btnsizer, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)

       btn = wx.Button(self, wx.ID_OK,'Close')
       btnsizer.AddButton(btn)
       btnsizer.Realize()

       self.SetSizer(sizer)
       sizer.Fit(self)

   def OnButton(self, evt):
       '''Handle button click event'''
       # Get title of clicked button
       label = evt.GetEventObject().GetLabel()

       if label == "Calculate Snow Factor for Spallation": # Calculate
           try:
               compute = math.exp(-float(self.thick.GetValue())*float(self.dens.GetValue())/float(self.att.GetValue()))
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
