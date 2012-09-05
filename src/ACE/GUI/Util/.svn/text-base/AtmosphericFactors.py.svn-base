"""
AtmosphericFactors.py

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

from pylab import load
from numpy import arange
from numpy import array
from scipy import ndimage

class Calculator(wx.Dialog):
   '''Main calculator dialog'''
   def __init__(self, repo):

       self.repo = repo

       wx.Dialog.__init__(self, None, -1, "Atmospheric Factors") 
       sizer = wx.BoxSizer(wx.VERTICAL) # Main vertical sizer

       # Latitude
       box = wx.BoxSizer(wx.HORIZONTAL) # Current calculation

       label = StaticFancyText(self, -1, "<FancyText>Sample Latitude (-90 -> 90 <sup>o</sup>)</FancyText>")
       box.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)

       self.lat = wx.TextCtrl(self, -1, "0", size=(80,-1))
       box.Add(self.lat, 1, wx.ALIGN_CENTRE|wx.ALL, 5)

       sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
       
       # Longitude
       box = wx.BoxSizer(wx.HORIZONTAL) # Current calculation

       label = StaticFancyText(self, -1, "<FancyText>Sample Longitude (0 -> 360 <sup>o</sup>)</FancyText>")
       box.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)

       self.lon = wx.TextCtrl(self, -1, "0", size=(80,-1))
       box.Add(self.lon, 1, wx.ALIGN_CENTRE|wx.ALL, 5)

       sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

       # [ Calculate Snow Factor Button Here ]
       c = wx.Button(self, -1, "Get Atmospheric Factors")
       self.Bind(wx.EVT_BUTTON, self.OnButton, c)
       sizer.Add(c, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
       self.equal = c
       
       # Answer box here
       box = wx.BoxSizer(wx.HORIZONTAL) # Current calculation

       label = StaticFancyText(self, -1, "Annual Sea Level Temperature ( <sup>o</sup>C )")
       box.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)

       self.sltemp = wx.ComboBox(self, -1) # Current calculation
       box.Add(self.sltemp, 1, wx.ALIGN_CENTRE|wx.ALL, 5)
       sizer.Add(box, 0, wx.ALIGN_CENTER_VERTICAL, 5)

       # Answer box here
       box = wx.BoxSizer(wx.HORIZONTAL) # Current calculation

       label = StaticFancyText(self, -1, "Annual Sea Level Pressure ( mb )")
       box.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)

       self.slprec = wx.ComboBox(self, -1) # Current calculation
       box.Add(self.slprec, 1, wx.ALIGN_CENTRE|wx.ALL, 5)
       sizer.Add(box, 0, wx.ALIGN_CENTER_VERTICAL, 5)

       # Answer box here
       box = wx.BoxSizer(wx.HORIZONTAL) # Current calculation

       label = StaticFancyText(self, -1, "Annual Lapse Rate ( -<sup>o</sup>C km<sup>-1</sup> )")
       box.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)

       self.lapse = wx.ComboBox(self, -1) # Current calculation
       box.Add(self.lapse, 1, wx.ALIGN_CENTRE|wx.ALL, 5)
       sizer.Add(box, 0, wx.ALIGN_CENTER_VERTICAL, 5)

       # Line
       line = wx.StaticLine(self, -1, size=(20,-1), style=wx.LI_HORIZONTAL)
       sizer.Add(line, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.TOP, 5)

       box = wx.BoxSizer(wx.HORIZONTAL) # Current calculation
       self._hyper1 = hl.HyperLinkCtrl(self, wx.ID_ANY, "Online Help",
                             URL="http://ace.hwr.arizona.edu/?page_id=18")
       box.Add(self._hyper1, 0, wx.ALIGN_CENTER_VERTICAL, 0)
      
       hspace = wx.StaticText(self, -1, " ")
       box.Add(hspace, 0, wx.ALIGN_CENTRE|wx.ALL, 5)

       self._hyper1 = hl.HyperLinkCtrl(self, wx.ID_ANY, "NCEP Data Description",                              URL="ftp://ftp.cdc.noaa.gov/Datasets/ncep.reanalysis.derived/README")
       box.Add(self._hyper1, 0, wx.ALIGN_CENTER_VERTICAL, 0)

       space = wx.StaticText(self, -1, " ")
       box.Add(space, 0, wx.ALIGN_CENTRE|wx.ALL, 5)

       btnsizer = wx.StdDialogButtonSizer()
       box.Add(btnsizer, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)

       btn = wx.Button(self, wx.ID_OK,'Close')
       btnsizer.AddButton(btn)
       btnsizer.Realize()
       sizer.Add(box, 0, wx.ALIGN_CENTER_VERTICAL, 5)

       self.SetSizer(sizer)
       sizer.Fit(self)

   def OnButton(self, evt):
       '''Handle button click event'''
       # Get title of clicked button
       label = evt.GetEventObject().GetLabel()

       if label == "Get Atmospheric Factors": # Calculate
           try:
               sampleLat = float(self.lat.GetValue())
               sampleLon = float(self.lon.GetValue())

               NCEP = load(self.repo.GetClimateDataPath())
               Temperature = NCEP[0:73,:];seaLevelPress = NCEP[73:146,:];
               LapseRate = NCEP[146:219,:];topo = NCEP[219:292,:]
               Temperature = NCEP[73:0:-1,:];seaLevelPress = NCEP[146:73:-1,:];
               LapseRate = NCEP[219:146:-1,:];topo = NCEP[292:73:-1,:]

               lat = arange(90,-91,-2.5);lon = arange(0, 361,2.5)

               #localCoords is the site coordinates relative to the NCEP data coords
               #For interpolation the field is considered to bound 1 -> nx-1 , 1 -> ny-1
               xfac = len(lat) - 1
               yfac = len(lon) - 1
               localX = (max(lat) - sampleLat) * xfac / (max(lat) - min(lat)) + 1
               localY = sampleLon / max(lon) * yfac + 1
               localCoords = array([[ localX],[ localY ]])

               AnnualMeanSLP = ndimage.map_coordinates(seaLevelPress, localCoords)
               AnnualMeanTemp = ndimage.map_coordinates(Temperature, localCoords)
               AnnualMeanLapse = ndimage.map_coordinates(LapseRate, localCoords)

               sltempVal = "%3.1f" % (float(AnnualMeanTemp))
               slprecVal = "%3.1f" % (float(AnnualMeanSLP))
               LapseRate = "%3.1f" % (float(AnnualMeanLapse*-1))

                # Ignore empty calculation
               #if not compute.strip():
               if not sltempVal:
                   return

               # Calculate result
               # result = eval(compute)

               # Add to history
               self.sltemp.Insert(str(sltempVal), 0)
               self.slprec.Insert(str(slprecVal), 0)
               self.lapse.Insert(str(LapseRate), 0)
              
               # Show result
               #self.display.SetValue(str(result))
               self.sltemp.SetValue(str(sltempVal))
               self.slprec.SetValue(str(slprecVal))
               self.lapse.SetValue(str(LapseRate))
               #self.slprec.SetValue(str(slprecVal))
           except Exception, e:
               wx.LogError(str(e))
               return

       else: # Just add button text to current calculation
           self.sltemp.SetValue(self.sltemp.GetValue() + label)
           self.equal.SetFocus() # Set the [=] button in focus

if __name__ == "__main__":
   # Run the application
   app = wx.PySimpleApp()
   dlg = Calculator()
   dlg.ShowModal()
   dlg.Destroy()
