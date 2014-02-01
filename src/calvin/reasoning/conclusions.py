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
import rule_list
    
def get(conclusion_name, core):
    #TODO -- set up a useful environment here
    conc = rule_list.required.get(conclusion_name, Conclusion(conclusion_name))
    conc.base_env['samples'] = core
    return conc

class Conclusion(object):
    """
    Conclusion Class
    Contains the symbol (name) of a specific instance of a conclusion plus 
    the list of arguments applicable to this specific conclusion 
    (like outlier x).
    Also represents the same thing but with arguments filled in 
    (like outlier 2).
    Properties
      name      - The name of the conclusion
      paramList - The list of the parameters

    Member functions
      buildEnv - Builds the initial enviroment from a filled conclusion.
    """
    def __init__(self, name, result=None, params=None, base={}):
        self.name = name
        self.result = result
        self.params = params
        self.base_env = base 
        
    def __eq__(self, other):
        """
        __eq__
        Equality is based on having the same name and same lengths
        """
        if isinstance(other, Conclusion):
            return self.name == other.name and \
                (not self.params and not other.params or \
                (self.params and other.params and
                 len(self.params) == len(other.params)))
        else:
            return False
        
    def __repr__(self):
        st = self.name.title()
        if self.params:
            st += ': ' + ', '.join([str(param) for param in self.params]) 
        return st
    
    def buildEnv(self, filledConc):
        """
        buildEnv()
        Builds an initial environment from this conclusion and a filled version
        of the same conclusion (passed as a parameter). 
        Initial environment values are also included in the result.
        Environments are dictionaries.
        Arguments 
        filledConc - A conclusion that is filled
        Returns : A dictionary representing an enviroment
        """
        
        if not self.params and not filledConc.params:
            # Paul changed this from self.base_env.copy()  
            return filledConc.base_env.copy()
        
        if not self.params or not filledConc.params or \
           len(filledConc.params) != len(self.params):
            print "TRIGGER VALUE ERROR"
            raise ValueError("Attempt to use a rule with incorrect number of "+
                             "conclusion parameters")
        
        env = dict(zip(self.params, filledConc.params))
        env.update(samples.initEnv)
        env.update(self.base_env)
        return env
        
    
class Result(object):
    """
    Result class
    Used to keep track of data that should be part of a conclusion.
    Maintains type data and has various retrieval convenience methods.
    Called in samples.py
    """
    def __init__(self, *args, **kwargs):
        kwargs.update(dict(args))
        self._data = kwargs
        self.result = dict.fromkeys(self._data)
        
    def __iter__(self):
        return self._data.iteritems()
        
    def __str__(self):
        suggest = ',\n'.join(['For {}: {}'.format(key, value) for key, value in 
                              self.result.items() if value is not None])
        if suggest:
            return 'I suggest using the following values:\n{}'.format(suggest)
        else:
            return 'Sorry, I am not smart enough to figure out what values to use'

