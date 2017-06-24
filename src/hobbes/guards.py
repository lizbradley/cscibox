"""
guards.py

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

module for guards on rules. This is in its own module so that special-purpose functions for
guards can be defined here rather than cluttering up some other module.
"""


class Guard(object):
    """
    Represents the guard on a rule, determining whether it can run
    """
    
    def __init__(self, fetch, params, compare,
                 comparison=lambda x, y: x == y,
                 invert=False):
        """
        Represents the guard on a rule. Requires the function to call to get the data to be
        checked, the parameters to that function, and what value the returned data is to be 
        compared to. Comparison is for equality by default, but other comparison functions
        may be passed instead. Order of call for these comparison functions is returned data,
        compare value.
        """
        self.fetch = fetch
        self.params = params
        self.compare = compare
        self.comparison = comparison
        self.invert = invert
        
        
    def passed(self, env):
        try:
            params = [parm in env and env[parm] or parm for parm in self.params]
            val = self.fetch(*params)
        except KeyError:
            return self.invert
        
        cm = self.comparison(val, self.compare in env and env[self.compare] or self.compare)
        if self.invert:
            return not cm
        return cm
    
