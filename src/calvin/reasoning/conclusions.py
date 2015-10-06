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

class Conclusion(object):
    """
    Contains the symbol (name) of a specific instance of a conclusion plus
    the list of arguments applicable to this specific conclusion
    (like outlier x).
    Also represents the same thing but with arguments filled in
    (like outlier 2).
    """
    def __init__(self, name, *params):
        self.name = name
        #TODO: make sure params is always hashable.
        self.params = tuple(params)
        
    def canfill(self, other):
        """
        One conclusion can fill another iff they have the same name-symbol and
        the same lengths, yo.
        """
        return isinstance(other, Conclusion) and self.name == other.name and \
            len(self.params) == len(other.params)

    def __eq__(self, other):
        """
        Equality is based on having the same name and parameter set
        """
        return isinstance(other, Conclusion) and self.name == other.name and \
            self.params == other.params

    def __repr__(self):
        st = self.name.title()
        if self.params:
            st += ': ' + ', '.join([str(param) for param in self.params])
        return st

    def update_env(self, working_env, filler):
        """
        updates a working environment with the conclusion-fillers in fill
        """
        if len(filler.params) != len(self.params):
            raise ValueError("Attempt to use a rule with incorrect number of "
                             "conclusion parameters")
        
        working_env.new_rule(self, filler)
        return working_env
    