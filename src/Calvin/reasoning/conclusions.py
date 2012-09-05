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

conclusions = ["no process", 
               'exhumation',
               #'clast erosion', #applies only when bedrock?
               "inheritance", 
               "vegetation cover", 
               "snow cover", 
               "outlier"]#,
               #'systematic error', 
               #'sheep']
special = {"outlier":__ALL_SAMPLES}
    
def reset():
    """
    Resets the conclusion state for starting up a new set of samples.
    Call this in between each thingymajig
    """
    global curState
    curState = 0

def getConclusions():
    """
    this function returns the list of conclusions that the engine should argue about. All
    parameters should be pre-entered.
    """
    
    #can't do this with a list comprehension. Sigh.
    result = []
    for conclusion in conclusions:
        if conclusion in special:
            result.extend(__fillParams(conclusion))
        else:
            result.append(Conclusion(conclusion))
    
    return result

    
def __fillParams(conclusion):
    """
    fills in parameters for conclusions and then returns the appropriate list of conclusion objects 
    based on the type ID passed in.
    """
    
    #conclusions should never be passed here anymore unless they're special ones
    
    if special[conclusion] == __ALL_SAMPLES:
        return [Conclusion(conclusion, [sample]) for sample in samples.sampleList]

class Conclusion:
    """
    Contains the symbol (name) of a specific instance of a conclusion plus the list of arguments
    applicable to this specific conclusion (like outlier x).
    
    Also represents the same thing but with arguments filled in (like outlier 2)
    """
    def __init__(self, name, paramList = None):
        self.name = name
        self.paramList = paramList
        if paramList is not None and len(paramList) == 0:
            self.paramList = None
        
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
            st += ': ' + ', '.join([str(param) for param in self.paramList]) #+ ')'
        return st
    
    def buildEnv(self, filledConc):
        """
        builds an initial environment from this conclusion and a filled version of the
        same conclusion (passed as a parameter). Initial environment values are also
        included in the result. Environments are dictionaries.
        """
        
        if self.paramList is None and filledConc.paramList is None:
            return samples.initEnv.copy()
        
        if self.paramList is None or \
           filledConc.paramList is None or \
           len(filledConc.paramList) != len(self.paramList):
            raise ValueError("Attempt to use a rule with incorrect number of conclusion parameters")
        
        env = dict(zip(self.paramList, filledConc.paramList))
        
        env.update(samples.initEnv)
        
        #if self.name == 'representative sample' or self.name == 'outlier':
        #    print self, env
        return env
        
    

        
