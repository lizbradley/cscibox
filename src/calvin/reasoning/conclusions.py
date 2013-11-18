"""
conclusions.py

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

#import confidence
import samples

__ALL_SAMPLES = 0

curState = 0

conclusions = ["reservoir adjustment", ]
special = {}
    
"""
reset()
Resets the conclusion state for starting up a new set of samples.
Call this in between each thingymajig ??
"""
def reset():
    global curState
    curState = 0

"""
getConclusions()
This function returns the list of conclusions that the engine should argue
about. All parameters should be pre-entered.
Returns : A list of conclusion objects ??
"""
def getConclusions():
    result = []
    for conclusion in conclusions:
        if conclusion in special:
            result.extend(__fillParams(conclusion))
        else:
            result.append(Conclusion(conclusion))
    return result

    
"""
__fillParams
Fills in parameters for conclusions and then returns the appropriate 
list of conclusion objects based on the type ID passed in.
Arguments
conclusion - A conclusion object to be filled (depricated?) ??
Returns : If the conclusion is special return a conclusion for each sample in
        * sampleList
"""
def __fillParams(conclusion):
    #conclusions should never be passed here anymore unless they're special 
    if special[conclusion] == __ALL_SAMPLES:
        return [Conclusion(conclusion, [sample]) for 
                sample in samples.sample_list]

"""
Conclusion Class
Contains the symbol (name) of a specific instance of a conclusion plus 
the list of arguments applicable to this specific conclusion (like outlier x).
Also represents the same thing but with arguments filled in (like outlier 2).
Properties
  name      - The name of the conclusion
  paramList - The list of the parameters

Member functions
  buildEnv - Builds the initial enviroment from a filled conclusion.
"""
class Conclusion:
    def __init__(self, name, paramList=None):
        self.name = name
        self.paramList = paramList
        if paramList is not None and len(paramList) == 0:
            self.paramList = None
    """
    __eq__
    Equality is based on having the same name and same lengths
    """
    def __eq__(self, other):
        if isinstance(other, Conclusion):
            return self.name == other.name and \
                (self.paramList is None and other.paramList is None or \
                (self.paramList is not None and other.paramList is not None and
                 len(self.paramList) == len(other.paramList)))
        else:
            return False
        
    def __repr__(self):
        st = self.name.title()
        if self.paramList is not None:
            st += ': ' + ', '.join([str(param) for param in self.paramList]) 
        return st
    
    """
    buildEnv()
    Builds an initial environment from this conclusion and a filled version
    of the same conclusion (passed as a parameter). Initial environment values
    are also included in the result. Environments are dictionaries.
    Arguments 
    filledConc - A conclusion that is filled
    Returns : A dictionary representing an enviroment
    """
    def buildEnv(self, filledConc):
        
        if self.paramList is None and filledConc.paramList is None:
            return samples.initEnv.copy()
        
        if self.paramList is None or \
           filledConc.paramList is None or \
           len(filledConc.paramList) != len(self.paramList):
            raise ValueError("Attempt to use a rule with incorrect number of "+
                             "conclusion parameters")
        
        env = dict(zip(self.paramList, filledConc.paramList))
        
        env.update(samples.initEnv)
        
        #if self.name == 'representative sample' or self.name == 'outlier':
        #    print self, env
        return env
        
    

        
