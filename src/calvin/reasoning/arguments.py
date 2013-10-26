"""
arguments.py

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
import evidence

"""
Argument Class
This happy class represents a complete argument. It holds the collection of
trees and can do the obvious thing where it calculates its confidence and
stuffs.
Properties
  conclusion - The conclusion being supported ?
  evidence   - A list of the rules supporting this argument
  conflict   - TODO
  confidence - The amount of confidence we have in this argument

Member functions
  toEvidence      - Returns the evidence.Argument(self)
  __setConfidence - Sets the confidence of this arguments conclusion
  getSingleConfidence - Returns the confidence
"""
class Argument:
        
    """
    __init__
    Arguments
    Creates a new Argument object from a list of Rule objects that have
    been run and stuffs.
    conclusion - An argument tat represents a conclusion
    runRules   - A list of rules to run, runs them if they have a confidence
               * and has yet to be run.  Runs the toEvidRule() member function
               * of rule
    """
    def __init__(self, conclusion, runRules):
        self.conclusion = conclusion
        #this is likely to be fixable.
        #if self.conclusion.name == 'likely age':
           # print self.conclusion, runRules
           # print runRules[0].wasRun(), runRules[0].getConfidence()
        self.evidence = [
            rule.toEvidRule() for rule in runRules 
            if rule.wasRun() and rule.getConfidence() is not None
        ]
        self.conflict = False
        self.__setConfidence()

    def toEvidence(self):
        return evidence.Argument(self)
                               
    def __repr__(self):
        return 'Argument about ' + str(self.conclusion) + \
               '\n Evidence is: ' + str(self.confidence) 

    """
    __setConfidence
    Sets the confidence in this argument's conclusion
    """
    def __setConfidence(self):
        if len(self.evidence) == 0:
            #if there is no evidence of any kind for the argument, then
            #there we can't put a valid confidence on the argument, no?
            #print "okay, doing this..."
            self.confidence = None
        else:
            self.confidence = confidence.Confidence.combine(
                    [rule.confidence for rule in self.evidence])
            if any([rule.confidence.valid > self.confidence.valid for 
                   rule in self.evidence]):
                self.conflict = True
            
        
    """
    getSingleConfidence
    Returns my happy confidence. Here for all kinds of good O-O reasons.
    """
    def getSingleConfidence(self):
        return self.confidence
    

        
        
        
