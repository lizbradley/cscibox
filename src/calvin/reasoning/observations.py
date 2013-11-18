"""
observations.py

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


#this module contains all the functions that do various sorts of simple things to observed data
import samples
import confidence as conf

def __howDif(a, b):
    if type(a) == type("") or type(b) == type(""):
        #one of my variables never got resolved, so I'm missing
        #that piece of input data
        raise KeyError()
    #print a, b
    percent = __calcPercent(a, b)
    
    if percent < .05:
        return conf.Applic.dt
    elif percent < .1:
        return conf.Applic.ft
    else:
        return conf.Applic.ct
    
def __calcPercent(a, b):
    if a is None or b is None:
        raise KeyError()
    print a, b
    div = a + b
    return (div != 0 and float(abs(a - b)) / div or 0)

def lt(a, b):
    dif = __howDif(a, b)
    return a < b and dif or -dif
lt.userDisp = {'infix':True, 'text':'<'}

def gt(a, b):
    dif = __howDif(a, b)
    return a > b and dif or -dif
gt.userDisp = {'infix':True, 'text':'>'}

def gte(a, b):
    if a == b:
        return conf.Applic.dt
    else:
        return gt(a, b)
gte.userDisp = {'infix':True, 'text':'>='}

def lte(a, b):
    if a == b:
        return conf.Applic.dt
    else:
        return lt(a, b)
lte.userDisp = {'infix':True, 'text':'<='}

def eqs(a, b):
    if a is None or b is None:
        raise KeyError()

    if a == b:
        return conf.Applic.ct
    else:
        return conf.Applic.cf
eqs.userDisp = {'infix':True, 'text':'='}

def neareq(a, b):
    percent = __calcPercent(a, b)
    
    if percent < .05:
        return conf.Applic.ct
    elif percent < .1:
        return conf.Applic.ft
    elif percent < .2:
        return conf.Applic.dt
    elif percent < .5:
        return conf.Applic.df
    elif percent < 1:
        return conf.Applic.ff
    else:
        return conf.Applic.cf
neareq.userDisp = {'infix':True, 'text':'=~'}

def sameMagnitude(a, b):
    if a == 0:
        a = 1
    if b == 0:
        b = 1
        
    if a < b:
        dif = float(b) / a
    else:
        dif = float(a) / b
    
    return lt(dif, 2)
sameMagnitude.userDisp = {'infix':True, 'text':'is the same magnitude as'}

def observed(item, spare=None):
    """
    checks whether the item was observed and, if so, returns whether it was observed in
    the positive or negative
    """ 
    
    if item is None or not item:
        return conf.Applic.cf
    else:
        return conf.Applic.ct
observed.userDisp = {'infix':False, 'text':'observed'}

def forAll(fcn, fName, parms=None):
    return __applyToAll(fcn, fName, parms, min)
forAll.userDisp = {'infix':False, 'text':'for all samples'}

def thereExists(fcn, fName, parms=None):
    return __applyToAll(fcn, fName, parms, max)
thereExists.userDisp = {'infix':False, 'text':'there exists a sample where'}

def majority(fcn, fName, parms=None):
    fun = globals()[fcn]
    
    count = sum([__trueCount(x) for x in 
                 [fun(sample[fName], parms) for sample in samples.sample_list]])
    
    return gte(count, len(samples.sample_list) / 2)
majority.userDisp = {'infix':False, 'text':'for most samples'}
                 
def __trueCount(x):
    if x.isTrue():
        return 1
    else:
        return 0
    
def __applyToAll(fcn, fName, parms, reduction):
    """
    for every sample, applies fcn (passed as a string and in this module) to that sample's value
    for fName and whatever other value fcn takes (since everything here is a comparison, things
    always take 2 values...)
    reduces all confidences according to reduction
    """
    fun = globals()[fcn]
    
    val = reduction([fun(sample[fName], parms) for sample in samples.sample_list])
    return val
