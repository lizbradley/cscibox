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

import types

import engine
import conclusions
import calculations
import observations
import simulations
import confidence
import evidence

ruleList = []

def makeRule(conclusion, rhsList, quality, guard=None, template=confidence.Template()):
    """
    Adds a new rule to the list of rules the system knows about.
    """
    ruleList.append(Rule(conclusion, guard, rhsList, quality, template))
    
def getRules(conclusion):
    """
    Returns the list of all rules with the appropriate conclusion name 
    and number of arguments
    """
    return [rule for rule in ruleList if rule.conclusion == conclusion]



class RightHandSide:
    """
    Base class for the rhses in rule Horn clauses. Contains all the stuff 
    that applies to everyone.
    
    This class is abstract.
    """
    def __init__(self, name, params, type):
        """
        name is the name of the function/argument used by this RHS.
        Should be a string.  params is a list of strings/values that
        should be sent to the function (or added to the argument conclusion) 
        when this RHS is "run"
        """
        self.name = name
        self.params = params
        self.type = type
        self.confidence = None
            
    def run(self, env):
        """
        "runs" this RHS appropriately and then sets the confidence. 
        Env should be the current, rule-local environment.
        Items in params will be replaced before running this RHS.
        """
        return self.type(self, env)
    
    class _RHSInstance:
        """
        Holds all the state information for a given RHS 
        (so that the RHS itself remains the same as each RHS is run)
        """
        
        def __init__(self, rhs, env, module=None):
            
            self.name = rhs.name
            self.params = rhs.params
            self.module = module
            self.confidence = None
            
            self.run(env)
                
        def run(self, env):
            """
            "runs" this RHS appropriately and then sets the confidence. 
            env should be the current, rule-local environment. 
            Items in params will be replaced before running this RHS.
            """
            raise NotImplementedError("RHSInstance is an abstract class and should not be instantiated")
            
        def _useEnv(self, env):
            """
            updates this RHS's parameters to replace items in the environment 
            with their values
            env should be a dictionary.
            """
            #TODO: fix this!
            #incredibly awful hack because deadlines. The right solution here
            #is to update a whole bunch of thinking about environments and stuff
            #so this happens in a sane and reasonable way. in the meantime... 
            samples.sample_list = env['samples']
            self.useParams = self.__convParams(env, self.params)
            
        def __convParams(self, env, paramList):
            #this handles the "normal" case where parameters just need to be replaced as well as the
            #"special" case where the parameter is actually a function call meant to be 
            #executed as this
            #rhs is being run. Could probably be done as a list comprehension but would be unreadable.
            
            if not paramList:
                return None
            
            tmp = []
            for param in paramList:
                if type(param) == types.TupleType:
                    #run this function (param[0]) using the parameters given
                    #(param[1], converted by this function
                    if len(param) > 1:
                        val = param[0](*self.__convParams(env, param[1]))
                    else:
                        val = param[0]()
                    
                else:
                    #replace the parameter with itself (if it is not an assigned
                    #variable) or with its assigned value (if it is in the environment)
                    val = param not in env and param or env[param]
            
                tmp.append(val)
        
            return tmp
            
        def _callFunction(self, env):
            """
            calls the function defined by 'self.module' and 'self.name' 
            with this RHS's parameter list. 
            Returns any value returned by the function.
            """
            print "IN CALL FUNCTION"
            
            try:
                print "Further in"
                self._useEnv(env)
                self.function = getattr(self.module, self.name)
                rslt = self.function(*self.useParams)
                return [rslt]
            
            except KeyError:
                #Missing some input data: set confidence = None
                self.confidence = None
                return False
            
        def toEvidence(self):
            """
            After this RHS has been 'run', returns a static evidence object 
            holding the information to display the run rhs to the user
            """
            raise NotImplementedError("RHSInstance is an abstract class and should not be instantiated")
        
        def valid(self, default=True):
            return self.confidence is not None

class Calculation(RightHandSide):
    """
    Calculation RHS
    """
    
    def __init__(self, name, params, varName):
        RightHandSide.__init__(self, name, params, self.__CalcInstance)
        self.varName = varName
        
    
    class __CalcInstance(RightHandSide._RHSInstance):
        
        def __init__(self, rhs, env):
            self.varName = rhs.varName
            RightHandSide._RHSInstance.__init__(self, rhs, env, calculations)
            
            
        def run(self, env):
            """
            Calculations update the environment; they have no confidence at all
            """
            self.value = self._callFunction(env)
            if self.value:
                self.value = self.value[0]
                env[self.varName] = self.value
                self.confidence = None
                
        def toEvidence(self):
            return evidence.Calculation(self)
        
        def valid(self, default=True):
            return default
        

class Observation(RightHandSide):
    """
    Observation RHS
    """
    def __init__(self, name, params):
        RightHandSide.__init__(self, name, params, self.__ObsInstance)
            
    class __ObsInstance(RightHandSide._RHSInstance):
        def __init__(self, rhs, env):
            RightHandSide._RHSInstance.__init__(self, rhs, env, observations)
            
        def toEvidence(self):
            return evidence.Observation(self)
            
        def run(self, env):
            """
            Observations are super-duper simple: run the function, 
            keep the confidence.
            """
            rslt = self._callFunction(env)
            #if self.name == 'lt':
            #    print self.params
            #    print rslt
            if rslt:
                rslt = rslt[0]
                self.confidence = confidence.Confidence(rslt, confidence.Validity.accept)
            
        
            
class Simulation(RightHandSide):
    """
    Simulation RHS
    """
    
    def __init__(self, name, params):
        RightHandSide.__init__(self, name, params, self.__SimInstance)
    
    class __SimInstance(RightHandSide._RHSInstance):
        def __init__(self, rhs, env):
            self.simResult = None
            RightHandSide._RHSInstance.__init__(self, rhs, env, simulations)
            
        
        def toEvidence(self):
            return evidence.Simulation(self)
            
        def run(self, env):
            """
            Simulations are complicated; they return a SimResult object
            """
            print "RUNNING A SIM"
            rslt = self._callFunction(env)
            if rslt:
                self.simResult = rslt[0]
                self.confidence = self.simResult.getConfidence()


class Argument(RightHandSide):
    """
    Argument RHS
    """
    def __init__(self, name, params=None):
        RightHandSide.__init__(self, name, params, self.__ArgInstance)
    
    
    class __ArgInstance(RightHandSide._RHSInstance):
        def toEvidence(self):
            return evidence.Argument(self.argument, self.params)
        
        def run(self, env):
            """
            So this is different because we don't call some function 
            and then do something with the result. 
            Instead, we need to call the engine and construct a new, 
            complete argument for the conclusion listed in name.
            """
            self._useEnv(env)
            self.argument = engine.buildArgument(conclusions.Conclusion(self.name, self.useParams))
            self.confidence = self.argument.getSingleConfidence()
            
        def toList(self):
            return self.argument.toList()
    


class Rule:
    """
    Object that defines a complete rule (Horn clause/implication).
    contains the conclusion, any prerequisites, the rhses and the confidence 
    combination information.
    """
    
    def __init__(self, conclusion, guard, rhsList, quality, confTemplate):
        """
        Makes a new rule.
        """
        self.conclusion = conclusion
        self.guard = guard
        self.rhsList = rhsList
        self.quality = quality
        self.confTemplate = confTemplate
       
    def canRun(self, conclusion):
        """
        evaluates the prerequisites. Returns true if all prereqs are met.
        """
        
        #if we're checking this, it's because we're running the rule anew and stuff
        self.ran = False
        
        if self.guard is None:
            return True
        else:
            env = self.conclusion.buildEnv(conclusion)
            return self.guard.guardPassed(env)
        
    def run(self, filledConc):
        """
        "runs" this rule by "running" all its RHSes (recursively, 
        as appropriate)
        """
        if not self.canRun(filledConc):
            raise UnrunnableRule(self.conclusion.name)
        
        return self.__RuleInstance(self, filledConc)
    
    class __RuleInstance:
        """
        Class that contains all the 'state' information of a rule that is 
        being run or has been run.
        """
        
        def __init__(self, rule, filledConc):
            """
            Makes a new rule.
            """
            self.conclusion = rule.conclusion
            self.quality = rule.quality
            self.confTemplate = rule.confTemplate
            self.confidence = None
            self.ran = False
            
            self.run(rule.rhsList, filledConc)
           
        def toEvidRule(self):
            return evidence.EvidRule(self)
            
        def wasRun(self):
            return self.ran
            
        
        def run(self, rhsList, filledConc):
            """
            "runs" this rule by "running" all its RHSes 
            (recursively, as appropriate)
            """
            env = self.conclusion.buildEnv(filledConc)
            self.filledConclusion = filledConc
        
            self.rhsList = []
            #rhses are run in order.
            for rhs in rhsList:
                self.rhsList.append(rhs.run(env))
                
            if self.confTemplate.priority:
                agg = all
            else:
                agg = any
                
            #bug: if a rule has a calculation that works and nothing else, it
            #works just fine...
                
            if agg([rhs.valid(self.confTemplate.priority) for rhs in self.rhsList]):    
                """
                this rule is only interesting if at least some of
                its input data actually existed...

                okay, so really what this ought to do is claim we 
                failed to run *unless* all rhses of the non-calculation type 
                worked.
                
                hrm, that's still insufficient. Think.
                """
                self.__setConfidence()   
                self.ran = True
            
        def __setConfidence(self):
            """
            sets the confidence in this rule after it has been run. 
            Used for efficiency purposes and stuff.
            """
            self.confidence = self.confTemplate.unify(self.quality,
                                        [rhs.confidence for rhs in self.rhsList if rhs.confidence])
                
        def getConfidence(self):
            """
            Returns the confidence that this rule adds 
            to the overall confidence in the conclusion of this rule.
            """
            return self.confidence
    
class UnrunnableRule(Exception):
    """
    Raised when someone tries to run a rule that cannot, in fact, be run 
    according to its prerequisites. Used so I don't get all confused-like
    """
    
    def __init__(self, conc):
        self.conc = conc
    
    def __str__(self):
        return "Cannot run rule with conclusion %s: prerequisites not met" % self.conc
    
    
    
    
    
