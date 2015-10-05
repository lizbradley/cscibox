"""
calculations.py

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

#forces all division to be floating-point
from __future__ import division
import numpy as np
import scipy.integrate as integrate
import confidence

class PeakComparison(object):
    def __init__(self,list_of_dictionaries):
        self.info = list_of_dictionaries

    def within(self,current_shape_differential):
        '''
        self is the range determined by other 3 depth intervals
        output : normal or not
        return applicabilities. How normal is this?
        '''
        return confidence.Applicability.highlyfor

class GaussianThreshold(object):
    def __init__(self, mean, variation):
        self.mean = mean
        self.variation = variation
    
    def __lt__(self, value, perc):
        # P will be the probability that the Gaussian variable is less then "value"
        mu = self.mean
        sigma = np.sqrt(self.variation) 
        pdf = lambda t: 1/(sigma*np.sqrt(2*np.pi))*np.exp((t-mu)**2/(2*sigma**2))
        P = .5 + integrate.quad(pdf,mu,float(value))[0]
        # determine the "applicability"
        strictness = min(abs(perc),abs(1-perc))
        if P >= perc:
            return confidence.Applicability.highlyfor
        elif (perc-P) <= strictness/2:
            # almost close enough
            return confidence.Applicability.weaklyfor
        elif (perc-P) <= strictness:
            # not very close
            return confidence.applicability.weaklyagainst
        else:
            # very far off
            return confidence.Applicability.highlyagainst
    def __le__(self, value, perc):
        # P will be the probability that the Gaussian variable is less then "value"
        mu = self.mean
        sigma = np.sqrt(self.variation) 
        pdf = lambda t: 1/(sigma*np.sqrt(2*np.pi))*np.exp((t-mu)**2/(2*sigma**2))
        P = .5 + integrate.quad(pdf,mu,float(value))[0]
        # determine the "applicability"
        strictness = min(abs(perc),abs(1-perc))
        if P >= perc:
            return confidence.Applicability.highlyfor
        elif (perc-P) <= strictness/2:
            return confidence.Applicability.weaklyfor
        elif (perc-P) <= strictness:
            return confidence.applicability.weaklyagainst
        else:
            return confidence.Applicability.highlyagainst
    def __gt__(self, value, perc):
        # P will be the probability that the Gaussian variable is less then "value"
        mu = self.mean
        sigma = np.sqrt(self.variation) 
        pdf = lambda t: 1/(sigma*np.sqrt(2*np.pi))*np.exp((t-mu)**2/(2*sigma**2))
        P = .5 - integrate.quad(pdf,mu,float(value))[0]
        # determine the "applicability"
        strictness = min(abs(perc),abs(1-perc))
        if P >= perc:
            return confidence.Applicability.highlyfor
        elif (perc-P) <= strictness/2:
            return confidence.Applicability.weaklyfor
        elif (perc-P) <= strictness:
            return confidence.applicability.weaklyagainst
        else:
            return confidence.Applicability.highlyagainst
    def __ge__(self, value, perc):
        # P will be the probability that the Gaussian variable is less then "value"
        mu = self.mean
        sigma = np.sqrt(self.variation) 
        pdf = lambda t: 1/(sigma*np.sqrt(2*np.pi))*np.exp((t-mu)**2/(2*sigma**2))
        P = .5 - integrate.quad(pdf,mu,float(value))[0]
        # determine the "applicability"
        strictness = min(abs(perc),abs(1-perc),.25)
        if P >= perc:
            return confidence.Applicability.highlyfor
        elif (perc-P) <= strictness/2:
            # we are almost close enough
            return confidence.Applicability.weaklyfor
        elif (perc-P) <= strictness:
            # we're sort of far away
            return confidence.applicability.weaklyagainst
        else:
            # we're really far away
            return confidence.Applicability.highlyagainst
    def __eq__(self, value, perc):
        pass
    def __ne__(self, value, perc):
        return Applicability.highlyfor

def synth_gaussian(core, mean, variation):
    return GaussianThreshold(mean, variation)


def past_avg_temp(core):
    return 'cake'

def find_peaks_per_proxy(core,depth_range):
    '''
    return a dictionary
    keys are names of proxies
    values are the number of peaks in that proxy, in the given depth range
    '''
    # call count_peaks for each proxy
    return 'donuts'

def get_normal_peak_behavior(core,depth_range):
    '''
    returns a peak comparison object
    '''
    # find peaks 3 times
    # give list of dictionaries? to peak comparison object creator
    # get current peak dict
    # object.within(current_peak_dict)
    myObject = PeakComparison(depth_range)
    return myObject

def count_peaks(core,depth_range,proxy_name,strictness=10):
    """
    The peak detection algorithm is originally from https://gist.github.com/endolith/250860
    I've modified it a bit ( - Kathleen)
    """
    
    depthlist = sorted(core.keys())
    
    return depthlist

    numPeaks = 0
           
    v = asarray(v)
        
    mn, mx = Inf, -Inf
    
    lookformax = True
    
    for i in arange(len(v)):
        this = v[i]
        if this > mx:
            mx = this
        if this < mn:
            mn = this

        if lookformax:
            if this < mx-delta:
                numPeaks += 1
                mn = this
                lookformax = False
        else:
            if this > mn+delta:
                mx = this
                lookformax = True

    return numPeaks

def number_of_peaks_is_normal(core,depth_interval):
    '''
    go back to half the depth
    look at 3 other depth intervals, each proxy series in those depth intervals
    see if your current interval has 'not enough bumps' in each data series, in comparison to 'normal'
    if current number of bumps per series is not normal, return evidence AGAINST
    if it IS normal,  return evidence FOR
    '''
    NormalPeaks = get_normal_peak_behavior(depth_interval)
    result = NormalPeaks.within(current_peak_behavior)
    return result
    

