"""
evidence.py

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


import confidence


#TODO: add display goodness herein (probably)
class Evidence(object):
    pass

class Observation(Evidence):
    def __init__(self, rhs, params, value):
        self.rhs = rhs
        self.filledparams = params
        self.value = value
        self.confidence = confidence.Confidence(self.value, confidence.Validity.accepted)
        
    def __str__(self):
        #TODO: this is assuming specifically binary comparison functions...
        funcstr = ' '.join(map(str, [self.rhs.params[0], self.rhs.name, self.rhs.params[1]]))
        if len(self.rhs.params) > 2:
            funcstr += ' (@ %s)' % ', '.join(map(str, self.rhs.params[2:]))
        #TODO: fill in values of all vars here, too...
        return funcstr

class Simulation(Evidence):
    """
    A Simulation should run a more complex function and then return
    the results.  What they should look like I have no idea
    """
    def __init__(self, rhs, paramset, result):
        self.rhs = rhs
        self.filledparams = paramset
        self.result = result
        self.confidence = self.result.confidence

class Argument(Evidence):
    def __init__(self, rhs, conclusion, argument):
        self.rhs = rhs
        self.conclusion = conclusion
        self.argument = argument
        self.confidence = argument.confidence
        self.evidence = argument.evidence
        
    def __repr__(self):
        return str(self)
        
    def __str__(self):
        argstr = 'Argument ' + str(self.confidence).replace('CONCLU', str(self.conclusion))
        return argstr + '\n  (' + '\n   '.join(map(str, self.evidence)) + ')'

class Rule(object):
    def __init__(self, rule, evidence, confidence):
        self.rule = rule
        self.evidence = evidence
        self.confidence = confidence
        
    def __repr__(self):
        return str(self)
        
    def __str__(self):
        implstr = 'Evidence ' + str(self.confidence).replace(
                        'CONCLU', str(self.rule.conclusion)) + ' <= ' + \
                    '\n '.join(map(str, self.evidence))
        return implstr
    


