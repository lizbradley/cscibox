"""
engine.py

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


import rule_list
import rules
import arguments
import confidence

def quick_confidence(conclusion, working_env):
    """
    runs 'quick' rules to do a first-pass over a conclusion to determine if it
    is worth pursuing further
    """
    #TODO: does this need to memo-ize based on env too? and if so, how do
    #I make sure to limit the yuck?
    cached = working_env.quick_cached(conclusion)
    if cached:
        return cached
    
    ruleset = rules.get_rules(conclusion)
    runset = []
    
    for rule in ruleset:
        runset.append(rule.quickrun(conclusion, working_env))
            
    result = confidence.parse_conf(runset)
    if result:
        working_env.quick_results[conclusion] = result
    return result

def build_argument(conclusion, working_env):
    """
    Builds an argument for the conclusion given. The conclusion should contain
    "filled" parameters, if it has any parameters.
    Arguments
    conclusion - A conclusion object to build the argument around
    Returns : An argument object
    """
    cached = working_env.cached(conclusion)
    if cached:
        return cached
        
    ruleset = rules.get_rules(conclusion)
    runset = []
    
    for rule in ruleset:
        runset.append(rule.run(conclusion, working_env))
            
    result = arguments.Argument(conclusion, working_env, runset)
    if result:
        working_env.memoized_results[conclusion] = result
    return result
    
##TODO: what does a param space search look like?
