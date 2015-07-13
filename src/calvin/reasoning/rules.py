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

def add_assumption(model, assumption, quality):
    """
    Builds a rule around assuming a particular state for a particular model
    """
    all_rules.append(Rule(conclusions.Conclusion('Use model %s' % model),
                          [Argument(assumption)], quality))

def add_rule(conclusion, rhs_list, quality, guard=None, template=confidence.Template()):
    """
    Adds a new rule to the list of rules the system knows about.
    """
    if not hasattr(rhs_list, '__iter__'):
        rhs_list = [rhs_list]
    all_rules.append(Rule(conclusion, rhs_list, quality, guard, template))
    
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
        
    def _callFunction(self, paramset):
        """
        calls the function defined by 'self.module' and 'self.name' 
        with this RHS's parameter list. 
        Returns any value returned by the function.
        """
        try:
            function = getattr(self.module, self.name)
            rslt = function(*paramset)
            return [rslt]
        except KeyError:
            return None

class Calculation(RightHandSide):
    """
    Calculation RHS

    These calculations should be simple and already defined.
    Check in calculation.py if you want to see the instances of them
    A calculation construction should look like this

    rules.Calculation('<calculationName>', [<argumentList>], <variableName>) 
    """
    
    def __init__(self, name, params, varName):
        super(Calculation, self).__init__(name, params, calculations)
        self.varName = varName
    
    def run(self, working_env, quick=False):
        #all calculations are quick
        paramset = working_env.fill_params(self.params)
        value = self._callFunction(paramset)
        if value:
            value = value[0]
            working_env.setvar(self.varName, value)
            return evidence.Calculation(self, paramset, value)

class Observation(RightHandSide):
    """
    Observation RHS

    The observations available can be found in observation.py
    observations look like this
    
    rules.Observation('<observationFunction>', [<Arguments>])
    """
    def __init__(self, name, params):
        super(Observation, self).__init__(name, params, observations)
        
    #TODO: this might want to look a bit different....
    def run(self, working_env, quick=False):
        #all observations are 'quick'...........
        paramset = working_env.fill_params(self.params)
        value = self._callFunction(paramset)
        if value:
            value = value[0]
            return evidence.Observation(self, paramset, value)
            
class Simulation(RightHandSide):
    """
    Simulation RHS

    Simulations are user defined functions that can assist a rule. 
    These functions must always return a SimResult object.
    They can be written in simulations.py
    Simulations look like this

    rules.Simulation('<simulationName>', [<argumentList>])
    """
    
    def __init__(self, name, params):
        super(Simulation, self).__init__(name, params, simulations)
        
    def run(self, working_env, quick=False):
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

    rules.Argument('<ruleName>')
    """
    def __init__(self, name, params=None):
        super(Argument, self).__init__(name, params)
        
    def run(self, working_env, quick=False):
        #TODO: may want to limit the degree of argument recursion when quick
        paramset = working_env.fill_params(self.params)
        conclusion = conclusions.Conclusion(self.name, params=paramset)
        if quick:
            return evidence.QuckArgument(self, conclusion, 
                             engine.quick_confidence(conclusion, working_env))
        else:
            return evidence.Argument(self, conclusion,
                             engine.build_argument(conclusion, working_env))

class Rule(object):
    """
    Object that defines a complete rule (Horn clause/implication).
    contains the conclusion, any prerequisites, the rhses and the confidence 
    combination information.
    """
    
    def __init__(self, conclusion, rhsList, quality, guard=None, confTemplate=confidence.Template()):
        self.conclusion = conclusion
        self.guard = guard
        self.rhs_list = rhsList
        self.quality = quality
        self.template = confTemplate
        
    def quickrun(self, conclusion, working_env):
        return self._do_run(conclusion, working_env, True)
    
    def run(self):
        return self._do_run(conclusion, working_env, False)
        
    def _do_run(self, conclusion, working_env, quick=False):
        self.conclusion.update_env(conclusion, working_env)
        if not self.guard.passed(env):
            working_env.leave_scope()
            return None
        
        evidence = []
        for rhs in self.rhs_list:
            evidence.append(rhs.run(working_env, quick))
        working_env.leave_scope()
                
        agg = all if self.template.priority else any
        if agg([evid and evid.valid(self.template.priority) for 
                evid in evidence]):
            confidence = self.template.unify(self.quality,
                    (evid.confidence for evid in evidence if evid and evid.confidence))
            return evidence.Rule(self, evidence, confidence)
        return None   
        
    
    
    
    
    
