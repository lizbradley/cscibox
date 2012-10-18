"""
BananaPlot.py

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
import math
import wx.lib.hyperlink as hl
from wx.lib.fancytext import StaticFancyText

from matplotlib.pylab import *

class Calculator(wx.Dialog):
   def __init__(self, sample1, sample2):
       self.lambdaStable = 1E-8
       self.lambda10Be = 4.5903788079470E-7
       self.lambda14C = 0.000120968
       self.lambda26Al = 9.68082654E-7
       self.lambda36Cl = 0.0000023028145533553

       #Choose whether to fill boxes with sample or test values
       if str(sample1["nuclide"]) == '3He':
         self.lambda1 = self.lambdaStable
       if str(sample1["nuclide"]) == '10Be':
         self.lambda1 = self.lambda10Be
       elif str(sample1["nuclide"]) == '14C':
         self.lambda1 = self.lambda14C 
       elif str(sample1["nuclide"]) == '21Ne':
         self.lambda1 = self.lambdaStable
       elif str(sample1["nuclide"]) == '26Al':
         self.lambda1 = self.lambda26Al
       elif str(sample1["nuclide"]) == '36Cl':
         self.lambda1 = self.lambda36Cl 

       if str(sample2["nuclide"]) == '3He':
         self.lambda2 = self.lambdaStable
       elif str(sample2["nuclide"]) == '10Be':
         self.lambda2 = self.lambda10Be #10Be by default
       elif str(sample2["nuclide"]) == '14C':
         self.lambda2 = self.lambda14C
       elif str(sample2["nuclide"]) == '21Ne':
         self.lambda2 = self.lambdaStable
       elif str(sample2["nuclide"]) == '26Al':
         self.lambda2 = self.lambda26Al
       elif str(sample2["nuclide"]) == '36Cl':
         self.lambda2 = self.lambda36Cl

       mu = 1.0/500.0 #Lal 1991

       #Banana plots are conventionally x-y plots, with the longer lived nuclide
       #concentration plotted on the x axis and the ratio of shorter lived to more
       #stable concentration plotted on the y axis.  So first we need to work out
       #which nuclide is longer lived.  Stability inversely proportional to lambda
       if (self.lambda1<self.lambda2):
         NOld=sample1["cosmogenic inventory"];
         NOldErr=sample1["cosmogenic inventory uncertainty"]
         POld=sample1["production rate invariant"]
         nuclideOld=str(sample1["nuclide"]);
         lambdaOld=self.lambda1;
         NYoung=sample2["cosmogenic inventory"];
         NYoungErr=sample2["cosmogenic inventory uncertainty"];
         PYoung=sample2["production rate invariant"];
         nuclideYoung=str(sample2["nuclide"]);
         lambdaYoung=self.lambda2;
       elif (self.lambda1>self.lambda2):
         NYoung=sample1["cosmogenic inventory"];
         NYoungErr=sample1["cosmogenic inventory uncertainty"]
         PYoung=sample1["production rate invariant"]
         nuclideYoung=str(sample1["nuclide"]);
         lambdaYoung=self.lambda1;
         NOld=sample2["cosmogenic inventory"];
         NOldErr=sample2["cosmogenic inventory uncertainty"];
         POld=sample2["production rate invariant"];
         lambdaOld=self.lambda2;
         nuclideOld=str(sample2["nuclide"]);
       else:
         dialog = wx.MessageDialog(None, 'Same Nuclide Species Selected', "Incorrect Sample Selection", wx.OK | wx.ICON_INFORMATION)
         dialog.ShowModal()
         return

       ax=subplot(111)
     
       #Plot the banana
       time= arange(10**floor(log10(NOld/10000)), 10.*(1/lambdaOld), 500)
       erosion=0
       YoungCoeff = lambdaYoung + mu * erosion;
       OldCoeff = lambdaOld + mu * erosion;
       NYoungtempN=PYoung/YoungCoeff*(1-exp(-time*YoungCoeff));
       NOldtempN=POld/OldCoeff*(1-exp(-time*OldCoeff));
       noe=semilogx(NOldtempN,NYoungtempN/NOldtempN,'r')
       hold(True)

       #Lower line second.  Time = Infinity
       erosion=arange(0.0, 1, 0.00001)
       YoungCoeff = lambdaYoung + mu * erosion;
       OldCoeff = lambdaOld + mu * erosion;
       NYoungtemp=PYoung/YoungCoeff
       NOldtemp=POld/OldCoeff
       sse=semilogx(NOldtemp,NYoungtemp/NOldtemp,'b')
    
       ageNoErosOld=-1/lambdaOld*log(1-lambdaOld*NOld/POld);
       NYoungNoEros=PYoung/lambdaYoung*(1-exp(-lambdaYoung*ageNoErosOld))
       ageNoErosYoung=-1/lambdaYoung*log(1-lambdaYoung*NYoung/PYoung);
       #If NYoungNoEros < NYoung, we are in the forbidden zone

       #At this point, also calculate how the ratio would look if it was
       #experiencing steady state erosion.  In this case the equations are
       #given by Lal.  ssErosion means Steady State Erosion

       ssErosion_num = lambdaYoung * NYoung * POld / NOld / PYoung - lambdaOld;
       ssErosion_den = mu * (1 - NYoung * POld / NOld / PYoung);
       ssErosion = ssErosion_num / ssErosion_den;
       ssNOld = POld / (lambdaOld + mu * ssErosion)

       #Calculate datapoint ellipse.  Will always need it
       theta = arange(0, 2*pi, 2*pi/1000)
       xellipse = NOld + NOldErr * cos(theta)
       yellipse = NYoung/NOld + sqrt((NYoungErr/NYoung)**2 + (NOldErr/NOld)**2) * sin(theta)

       if (NYoungNoEros < NYoung ):
         title('Forbidden Zone')

         h=semilogx([NOld],[NYoungNoEros/NOld],'gs',[NOld],[NYoung/NOld],'ro',label='last')
         legend((h),('Zero Erosion Ratio','Sample Ratio'),loc=3,numpoints=1)

         semilogx(xellipse,yellipse,'k')

       elif (NOld > ssNOld):
         title('Steady State Erosion')

         maxErosion = 1/mu * (PYoung / NYoung - lambdaYoung);

         precision = 1000; #User should probably be able to change this value
         res = zeros(precision)
         modeltime = zeros(precision)
         modelerosion = zeros(precision)

         realErosion = arange(0.0, maxErosion, maxErosion/precision)
         YoungCoeff = lambdaYoung + mu * realErosion;
         OldCoeff = lambdaOld + mu * realErosion;
         YoungCoeff_time = -1/YoungCoeff * log(1-NYoung*YoungCoeff/PYoung);
         OldCoeff_time = -1/OldCoeff * log(1-NOld*OldCoeff/POld);

         res = abs(YoungCoeff_time-OldCoeff_time);
         modeltime = (YoungCoeff_time+OldCoeff_time)/2.0;
         modelerosion = realErosion;

         #The smallest value of res is the one closest to the true solution
         #If the residual is too high, increase the precision and slow down
         #the calculation

         minres = min(res)
         i=find(res==minres)
         realSampleAge = modeltime[i]
         YoungSampleAgeError = NYoungErr / (PYoung - NYoung * YoungCoeff[i]) 
         OldSampleAgeError = NOldErr / (POld - NOld * OldCoeff[i])
         realSampleAgeError = 0.5 * sqrt(YoungSampleAgeError **2 + OldSampleAgeError**2)
         realErosionRate = modelerosion[i]

         #Place the determined age and erosion rate on the plot
         textlabel = "Erosion age = %3.0f yr" % (1000*int(realSampleAge/1000))
         text(0.05, 0.5,textlabel,transform = ax.transAxes)
         textlabel = "Erosion rate = %6.5f cm/yr" % (realErosionRate/10)
         text(0.05, 0.4,textlabel,transform = ax.transAxes)

         #Plot the time history of this age and rate in 10 yr intervals
         time = arange(1.0, realSampleAge, 10)
         modelNOld= POld/OldCoeff[i]*(1-exp(-OldCoeff[i]*time));
         modelNYoung=PYoung/YoungCoeff[i]*(1-exp(-YoungCoeff[i]*time));
         semilogx(modelNOld,modelNYoung/modelNOld);

         timeOrder = 10**floor(log10(realSampleAge))
         #Plot the time history of this age and rate in 10^n yr intervals
         #where n is an integer
         time = arange(timeOrder, realSampleAge, timeOrder)
         modelNOld= POld/OldCoeff[i]*(1-exp(-OldCoeff[i]*time));
         modelNYoung=PYoung/YoungCoeff[i]*(1-exp(-YoungCoeff[i]*time));

         #Plot important symbols
         h=semilogx(modelNOld,modelNYoung/modelNOld,'s',[NOld],[NYoung/NOld],'ro')
         textlabel = str(int(timeOrder/1000)) + " kyr intervals"
         legend((h),(textlabel,'Sample Ratio'),loc=3,numpoints=1)

         semilogx(xellipse,yellipse,'k')

       else:
         title('Prior Exposure')

         #Calculate maximum possible recent exposure time
         maxretime=-1/lambdaYoung*log(1-NYoung*lambdaYoung/PYoung)
         NOldBurial=NOld-POld/lambdaOld*(1-exp(-lambdaOld*maxretime))

         #Put the maximum possible recent exposure time on the plot
         textlabel = "Maximum Recent Exposure  = " + str(int(round(maxretime))) + " yr"
         text(0.1, 0.1,textlabel,transform = ax.transAxes)

         #Plot the time history in 10 yr parts
         time = arange(0.0, maxretime, 10)
         modelNOld=POld/lambdaOld*(1-exp(-lambdaOld*time))+NOldBurial
         modelNYoung=PYoung/lambdaYoung*(1-exp(-lambdaYoung*time))
         semilogx(modelNOld,modelNYoung/modelNOld)

         #Plot the time history in 10^n parts (n integer)
         timeOrder = 10**floor(log10(maxretime,))
         time = arange(timeOrder, maxretime, timeOrder)
         modelNOld= POld/lambdaOld*(1-exp(-lambdaOld*time))+NOldBurial;
         modelNYoung=PYoung/lambdaYoung*(1-exp(-lambdaYoung*time));
  
         #Plot the data
         h=semilogx(modelNOld,modelNYoung/modelNOld,'s',[NOld],[NYoung/NOld],'ro')
         textlabel = str(int(timeOrder/1000)) + " kyr Intervals"
         legend((h),(textlabel,'Sample Ratio'),loc=1,numpoints=1)
  
         semilogx(xellipse,yellipse,'k')

       textlabel = str(nuclideOld) + " Inventory "
       xlabel(textlabel)
       textlabel = str(nuclideYoung) + "/" + str(nuclideOld) + " Inventory Ratio"
       ylabel(textlabel)
       xlim (10**(floor(log10(NOld/10))), 10**(ceil(log10(NOldtemp[1]))))
   
       grid(True)
       show()

if __name__ == "__main__":
   # Run the application
   app = wx.PySimpleApp()
   dlg = Calculator()
   dlg.ShowModal()
   dlg.Destroy()
