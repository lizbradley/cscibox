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


import itertools
import confidence
import operator

comparisons = {'<': '__lt__',
               '<=': '__le__',
               '>': '__gt__',
               '>=': '__ge__',
               '!=': '__ne__',
               '~=': 'near_eq',
               'within %': 'within_perc',
               'is true': 'istrue',
               'is the same magnitude as': 'same_mag'}

VERY_CLOSE = .05
CLOSE = .1
CLOSEISH = .2
FARISH = .5
FAR = .75
VERY_FAR = 1

def apply(fn_name, *params):
    if fn_name in comparisons:
        fn_name = comparisons[fn_name]
    if hasattr(params[0], fn_name):
        truth = getattr(params[0], fn_name)(*params[1:])
    else:
        try:
            func = globals()[fn_name]
        except KeyError:
            func = getattr(operator, fn_name)
        
        truth = func(*params)
        
    if hasattr(truth, 'level'):
        #little hacky, but basically our function already returned a truthy
        #value, which is what we needed here.
        return truth
    else:
        diff = _app_difference(*params)
        return diff if truth else -diff
        
        
def _app_difference(*params):
    #TODO: handle things like un-resolved vars?
    perc = _percent_difference(*params)
    
    if perc < VERY_CLOSE:
        return confidence.Applicability.partlyfor
    elif perc < CLOSE:
        return confidence.Applicability.mostlyfor
    else:
        return confidence.Applicability.highlyfor
    
def _percent_difference(*params):
    if not all(params):
        return 0
    params = map(float, params)
    divisor = sum(map(abs, params))
    if divisor == 0:
        return 1
    value = 0
    count = 0
    for a, b in itertools.combinations(params, 2):
        value += abs(a - b)
        count += 1
    return value / (divisor * count)

def within_perc(a, b, perc):
    '''
    checks if the percent error between a and b is less than 'perc'.
    Note that a is the divisor (the 'correct' number we are comparing against)
    '''
    percentError = abs((a-b)/a)
    if percentError <= perc:
        return confidence.Applicability.highlyfor
    elif (perc - percentError) < 0.05:
        return confidence.Applicability.mostlyfor
    elif (perc - percentError) < 0.1:
        return confidence.Applicability.partlyagainst
    elif (perc-percentError) < 0.3:
        return confidence.Applicability.mostlyagainst
    else:
        return confidence.Applicability.highlyagainst

def istrue(value):
    if value is None:
        return None
    return confidence.Applicability.highlyfor if value else \
        confidence.Applicability.highlyagainst
    
def near_eq(a, b):
    percent = _percent_difference(a, b)
    
    if percent < VERY_CLOSE:
        return confidence.Applicability.highlyfor
    elif percent < CLOSE:
        return confidence.Applicability.mostlyfor
    elif percent < CLOSEISH:
        return confidence.Applicability.partlyfor
    elif percent < FARISH:
        return confidence.Applicability.partlyagainst
    elif percent < FAR:
        return confidence.Applicability.mostlyagainst
    else:
        return confidence.Applicability.highlyagainst

def same_mag(a, b):
    if float(a) == float(b):
        return confidence.Applicability.highlyfor
        
    try:
        diff = float(a) / float(b)
    except ZeroDivisionError:
        diff = float(b) / float(a)
    
    #TODO: is this anything resembling right?
    return near_eq(diff * 100, 100)

