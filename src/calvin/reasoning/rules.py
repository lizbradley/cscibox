"""
rules.py

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

import engine
import conclusions
import calculations
import observations
import simulations
import confidence
import evidence

all_rules = []

def make_rule(conc, rhs_list, validity, template=()):
    if isinstance(conc, basestring):
        conc = [conc]
    if not hasattr(rhs_list, '__iter__'):
        rhs_list = [rhs_list]
    if not isinstance(template, confidence.Template):
        template = confidence.Template(*template)
    #TODO - old conclusions needed other params sometimes; do I still?
    all_rules.append(Rule(conclusions.Conclusion(*conc), rhs_list, validity, template))
    #TODO: guards; templates?
    
def get_rules(conclusion):
    """
    Returns the list of all rules with the appropriate conclusion name 
    and number of arguments
    """
    return [rule for rule in all_rules if rule.conclusion.canfill(conclusion)]



class RightHandSide(object):
    """
    Base class for the rhses in rule Horn clauses.  
    Describes the right hand side of a rule.
    Rules are run recursively starting from a top rule.
    Rules are composed of four basic types

    Simulation   - Runs a function defined in simulation.py
    Calculation  - Runs simple calculations defined in calculation.py 
    Observation  - Observes data from observation.py
    Argument     - Runs a sub rule recursively from rule_list.py

    This class is abstract.
    """
    def __init__(self, name, params=[], module=None):
        """
        name is the name of the function/argument used by this RHS.
        Should be a string.  params is a list of strings/values that
        should be sent to the function (or added to the argument conclusion) 
        when this RHS is "run"
        """
        self.name = name
        self.params = params
        self.module = module

class Observation(RightHandSide):
    """
    Observation RHS

    The observations available can be found in observation.py
    """
    def __init__(self, name, *params):
        self.name = name
        self.params = params
        
    def run(self, working_env):
        paramset = working_env.fill_params(self.params)
        try:
            value = observations.apply(self.name, *paramset)
        except:
            return None
        return evidence.Observation(self, paramset, value)
            
class Simulation(RightHandSide):
    """
    Simulation RHS

    Simulations are the way individual rules can reference computation plans.
    """
    
    def __init__(self, name, *params):
        self.name = name
        self.params = params
        
    def run(self, working_env, quick=False):
        #TODO: I think these are going to want to go on the 'delayed'/costly
        #stack and queue up for later, rather than running immediately...
        return None
        if quick:
            #simulations are never quick...
            return None
        paramset = working_env.fill_params(self.params)
        value = self._callFunction(paramset)
        if value:
            value = value[0]
            return evidence.Simulation(self, paramset, value)

class Argument(RightHandSide):
    """
    Argument RHS
    Runs a rule recursively from rule_list.py
    Arguments look like this :

    arg('<conclusion name>')
    #TODO: parameters?
    """
    def __init__(self, name, *params):
        self.name = name
        self.params = params
        
    def run(self, working_env):
        paramset = working_env.fill_params(self.params)
        conclusion = conclusions.Conclusion(self.name, *paramset)
        arg = engine.build_argument(conclusion, working_env)
        if arg.evidence:
            return evidence.Argument(self, conclusion, arg)

class Rule(object):
    """
    Object that defines a complete rule (Horn clause/implication).
    contains the conclusion, any prerequisites, the rhses and the confidence 
    combination information.
    """
    
    def __init__(self, conclusion, rhs_list, quality, confTemplate, guard=None):
        self.conclusion = conclusion
        self.guard = guard
        self.rhs_list = rhs_list
        self.quality = quality
        self.template = confTemplate
        
    def run(self, conclusion, env):
        working_env = self.conclusion.update_env(env, conclusion)
        if self.guard and not self.guard.passed(working_env):
            working_env.leave_rule()
            return None
        
        evid_list = []
        for rhs in self.rhs_list:
            evid_list.append(rhs.run(working_env))
        working_env.leave_rule()
                
        agg = all if self.template.priority else any
        if agg(evid_list):
            confidence = self.template.unify(self.quality,
                    (evid.confidence for evid in evid_list if evid and evid.confidence))
            return evidence.Rule(self, evid_list, confidence)
        return None   
        
    
    
    
    
    
