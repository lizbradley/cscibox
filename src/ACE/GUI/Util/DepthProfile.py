"""
DepthProfile.py

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
import numpy
import wx.lib.hyperlink as hl
from wx.lib.fancytext import StaticFancyText
from matplotlib.pylab import *

class Calculator(wx.Dialog):
   '''Main calculator dialog'''
   def __init__(self, sample):

       #Attenuations hardwired for now
       LAMBDA_f = 177.0
       LAMBDA_mu = 1500.0

       ax1 = subplot(111)
       ProfileDepth = arange(0, 50 * sample['density'], 1)
       if sample['production rate spallation'] != None:
         #Gosse and Phillips 2001 Equation 3.15
         spallation = sample['production rate spallation'] * exp(-ProfileDepth / LAMBDA_f)
         ax1.plot(spallation, -ProfileDepth / sample['density'], 'r', label="Spallation")
         #label = StaticFancyText(self, -1, "Production Rate (a g<sup>-1</sup> yr<sup>-1</sup>)")
         sum = spallation
         grid()

       if sample['production rate muons'] != 0:
         #Gosse and Phillips 2001 Equation 3.49
         muons = sample['production rate muons'] * exp(-ProfileDepth / LAMBDA_mu)
         ax1.plot(muons, -ProfileDepth / sample['density'], 'g', label='Muons')
         sum = sum + muons

       if sample['production rate low-energy'] != 0:
         S_th = sample['scaling low-energy']
         shielding_factor = sample['shielding factor']
         #Gosse and Phillips 2001 Equation 3.27
         epiFlux = sample['Phistar_eth_ss'] * exp(-ProfileDepth / LAMBDA_f) + \
                   sample['FDeltaPhistar_eth'] * exp(-ProfileDepth / sample['L_eth_ss'])
         epiThermal = S_th * shielding_factor * sample['f_eth'] / sample['LAMBDA_eth_ss'] * epiFlux

         #Gosse and Phillips 2001 Equation 3.37
         thermalFlux = sample['Phistar_th_ss'] * exp(-ProfileDepth / LAMBDA_f) + \
                       sample['FScrDeltaPhistar_eth_ss'] * exp(-ProfileDepth / sample['L_eth_ss']) + \
                       sample['FScrDeltaPhistar_th_ss'] * exp(-ProfileDepth / sample['L_th_ss'])
         thermal = S_th * shielding_factor * sample['f_th'] / sample['LAMBDA_th_ss'] * thermalFlux

         lowEnergy = thermal + epiThermal

         lowEnergy = sample['production rate low-energy'] / lowEnergy[0] * lowEnergy
         ax1.plot(lowEnergy, -ProfileDepth / sample['density'], 'b', label='Low Energy Neutrons')
         sum = sum + lowEnergy

       ax1.plot(sum, -ProfileDepth / sample['density'], 'k', label='Total')
       title('Time Averaged Production Rate Profile for ' + sample['id'])
       ax1.set_xlabel('Production Rate (atoms / g / yr)')
       ax1.set_ylabel('Depth below Surface (cm)')
       legend(loc=4) 
       show()

if __name__ == "__main__":
   # Run the application
   app = wx.PySimpleApp()
   dlg = Calculator(sample)
