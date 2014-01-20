"""
rule_list.py

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

#this module defines all my rules (right at the moment)
#eventually these may get split up, if they're too hard to deal with as one file :P

#need to add a for-all that calls an argument. whee.

import quantities

import rules
from conclusions import Conclusion, Result
from confidence import Validity


def __minusFun(x, y):
    if type(x) == str or type(y) == str:
        print x, y
    return x - y

def __plusFun(x, y):
    return x + y

def __mulFun(x, y):
    return x * y

def __divFun(x, y):
    if y == 0:
        return x
    else:
        return float(x) / y

__minusFun.userDisp = {'infix':True, 'text':'-'}
__plusFun.userDisp = {'infix':True, 'text':'+'}
__mulFun.userDisp = {'infix':True, 'text':'*'}
__divFun.userDisp = {'infix':True, 'text':'/'}

"""
Construction of a rule:

conclusion,
[list of rhs items]
rule quality (may be a tuple. if so, it is (quality if true, quality if false)
guard (may be missing),
confidence template (may be missing)

both guards and templates should be referenced by name, to avoid problems 
    (guard=, template=)

Conclusions: conclusion name, [optional list of conclusion parameters]
Guards: information retrieval function (NOT function name), [function parameters],
        comparison value, optional comparison function (NOT function name)
Templates contain: 
        priority - whether the confidences in the RHS are combined AND-style or OR-style
        increment - which direction and how much the match closeness is incremented
        flip - whether the true/falseness of the RHS combination is flipped

rhs items:
Observation: function name (in observations.py), [function parameters]
Calculation: function name (in calculataion.py), [function parameters], variable name for rest of rule
Simulation: function name (in simulations.py), [function parameters], variable name for rest of rule (may be None)
Argument: conclusion name, [optional list of conclusion parameters]

if any function parameter is a tuple, it is interpreted as a function to be run. The first value
should be the function to run (NOT function name), the second value should be a tuple of parameters
to the function.
"""


#top-level conclusions
#no process


#TODO: there's no particularly good or pythonic reason to have to put all this
#darn boilerplate in every rule; it would be better for the rule-making 
#function to have more and more-useful magic in it.

required = {'reservoir adjustment': Conclusion('reservoir adjustment', 
            result=Result(('Adjustment', float), ('+/- Adjustment Error', float)))}

rules.makeRule(Conclusion("reservoir adjustment"),
         [rules.Calculation('calcMax', ['depth'], 'max depth'),
          rules.Observation('gt',['max depth', 
          quantities.Quantity(1000, 'cm')])],
          Validity.sound)

