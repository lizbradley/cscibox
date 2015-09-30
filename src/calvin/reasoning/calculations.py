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

from __future__ import division
from confidence import Applicability
import numpy as np
import scipy.integrate as integrate

class GaussianThreshold(object):
    def __init__(self, mean, variation):
        self.mean = mean
        self.variation = variation
        pass
    
    def __lt__(self, value, perc):
        # P will be the probability that the Gaussian variable is less then "value"
        mu = self.mean
        # check this next line!!
        sigma = np.sqrt(self.variation) 
        pdf = lambda t: 1/(sigma*np.sqrt(2*np.pi))*np.exp((t-mu)**2/(2*sigma**2))
        P = .5 + integrate.quad(pdf,mean,value)[0]
        if P >= perc:
            return True
        else:
            return False
    def __le__(self, value, perc):
        pass
    def __gt__(self, value, perc):
        pass
    def __ge__(self, value, perc):
        pass
    def __eq__(self, value, perc):
        pass
    def __ne__(self, value, perc):
        return Applicability.highlyfor

def synth_gaussian(core, mean, variation):

    myObject = GaussianThreshold
    
    return 'cookies'


def past_avg_temp(core):
    return 'cake'
    

