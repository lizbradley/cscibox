"""
Nuclide.py

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

import os

class Nuclide(object):

    #Why give HLSL production rates here when they should be calibrated?
    #For non-36Cl nuclides, muon contributions are given as a percentage
    #of total production, which we don't know ahead of time.  For the values
    #below, 'absolute' muon contributions are calculated as specified percent
    #values times total production rates given below.  These contributions
    #are then removed from the observed inventory and a linear regression
    #for spallation is computed.  This is why pre and post calibrated 
    #muon percentages differ
    psi_spallation_total         = {}
    psi_spallation_total["3He"]  = 116.0 # Licciardi et al 19999
    psi_spallation_total["10Be"] = 4.98  # Balco and Stone 2007
    psi_spallation_total["14C"]  = 17.5  # Lifton pers comm
    psi_spallation_total["21Ne"] = 19.0  # Niedermann 2000
    psi_spallation_total["26Al"] = 30.6  # Balco and Stone 2007

    decay         = {}
    decay["3He"]  = 0.0
    decay["10Be"] = 4.5903788079470E-7
    decay["14C"]  = 0.000120968
    decay["21Ne"] = 0.0
    decay["26Al"] = 9.68082654E-7
    decay["36Cl"] = 2.30281E-6

    slow_muon_perc = {}
    slow_muon_perc["3He"]  = 0.0
    slow_muon_perc["10Be"] = 2.0
    slow_muon_perc["14C"]  = 15.0
    slow_muon_perc["21Ne"] = 0.0
    slow_muon_perc["26Al"] = 2.0

    fast_muon_perc = {}
    fast_muon_perc["3He"]  = 0.0
    fast_muon_perc["10Be"] = 2.0
    fast_muon_perc["14C"]  = 2.0
    fast_muon_perc["21Ne"] = 0.0
    fast_muon_perc["26Al"] = 2.0

    @staticmethod
    def stable(element):
        if element == "3He" or element == "21Ne":
            return True
        return False
    
    @staticmethod
    def getSlowMuonStoppingRate():
        return 175.0
    
    @staticmethod
    def getFastMuonFlux():
        return 700000.0
    
    @staticmethod
    def getSlowMuonPerc(nuclide):
        return Nuclide.slow_muon_perc[nuclide]

    @staticmethod
    def getFastMuonPerc(nuclide):
        return Nuclide.fast_muon_perc[nuclide]
         
    def __init__(self, name="DEFAULT"):
        self.element  = name
        self.required = []
        self.optional = []
        
    def add_optional(self, att):
        self.add_sorted(att, self.optional)

    def add_required(self, att):
        self.add_sorted(att, self.required)

    def add_sorted(self, att, atts):
        if att not in atts:
            atts.append(att)
            atts.sort()
        
    def contains(self, att):
        return (att in self.required) or (att in self.optional)
        
    def name(self):
        return self.element

    def remove_optional(self, att):
        self.optional.remove(att)

    def remove_required(self, att):
        self.required.remove(att)
        
    def required_atts(self):
        return self.required[:]

    def optional_atts(self):
        return self.optional[:]

    def save(self, f):
        f.write(self.element)
        f.write(os.linesep)
        f.write('BEGIN REQUIRED')
        f.write(os.linesep)
        for att in self.required:
            f.write(att)
            f.write(os.linesep)
        f.write('END REQUIRED')
        f.write(os.linesep)
        f.write('BEGIN OPTIONAL')
        f.write(os.linesep)
        for att in self.optional:
            f.write(att)
            f.write(os.linesep)
        f.write('END OPTIONAL')
        f.write(os.linesep)
