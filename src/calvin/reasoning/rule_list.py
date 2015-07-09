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

from rules import *
from conclusions import Conclusion
from confidence import Validity

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
Calculation: function name (in calculation.py), [function parameters], variable name for rest of rule
Simulation: function name (in simulations.py), [function parameters], variable name for rest of rule (may be None)
Argument: conclusion name, [optional list of conclusion parameters]

if any function parameter is a tuple, it is interpreted as a function to be run. The first value
should be the function to run (NOT function name), the second value should be a tuple of parameters
to the function.
"""


rules.add_assumption('Bacon', Conclusion('smooth change', ('accumulation rate',)), 
                     Validity.sound)

rules.add_rule(Conclusion('smooth change', 'variablething'), 
               '2nd derivative < x', Validity.sound)


