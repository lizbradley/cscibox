"""
evidence.py

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
import observations
import confidence

class Evidence:
    def __init__(self, rhs):
        self.name = rhs.name
        self.module = rhs.module
        self.params = rhs.params
        self.useParams = rhs.useParams
        self.confidence = rhs.confidence
        
    def __cmp__(self, other):
        slit = self.confidence.valid < confidence.Validity.prob
        olit = other.confidence.valid < confidence.Validity.prob
        if slit and not olit:
            return 1
        elif olit and not slit:
            return -1
        elif self.confidence.isTrue() and not other.confidence.isTrue():
            return -1
        elif not self.confidence.isTrue() and other.confidence.isTrue():
            return 1
             
        return (self.confidence.cmpMag(other.confidence))
    
    def _displayFormat(self, function, items, notStr='', env={}):
        if type(function) == types.StringType:
            function = getattr(self.module, function)
            
        if hasattr(function, 'userDisp'):
            
            display = function.userDisp
            
            if display['infix']:
                return ' '.join((self._formatVar(items[0], env), notStr + display['text'],
                                 self._formatVar(items[1], env)))
            else:
                disp = display['text'] + ' '
                #if the first item in the list is also a function, we should handle that.
                #this should only happen in this specific case.
                #print items[0]
                if len(items) > 0 and type(items[0]) == types.TupleType and len(items[0]) > 1:
                    return notStr + disp + self._displayFormat(items[0][0],
                                                      items[0][1], '', env)
                else:
                    return notStr + disp + ', '.join([self._formatVar(item, env) for item in items])
        
        else:
            #print function
            return function.func_name + self._formatVar(items, env)
        
    def _formatVar(self, var, env={}):
        if hasattr(var, '__iter__'):
            if len(var) > 1:
                return self._displayFormat(var[0], var[1], env=env)
            else:
                return self._displayFormat(var[0], [], env=env)
        elif var in env:
            return str(env[var])
        else:
            return str(var)
        
    def _formatParams(self):
        if len(self.params) > 0:
            return ' (' + ', '.join([self._formatVar(var) for var in self.params]) + ')'
        else:
            return ""
        
    def getToolTipText(self):
        return None
        
    @classmethod
    def hasExpansion(cls):
        return False
    
    @classmethod
    def isArgument(cls):
        return cls.__name__ == "Argument"
    
    @classmethod
    def isSimulation(cls):
        return cls.__name__ == "Simulation"
    
    @classmethod
    def isCalculation(cls):
        return cls.__name__ == "Calculation"
    
    def getRuleString(self, env={}):
        raise NotImplementedError("Evidence is an abstract class and should not be instantiated")
        
    def getUnifiedString(self):
        raise NotImplementedError("Evidence is an abstract class and should not be instantiated")
          

class Calculation(Evidence):
    
    def __init__(self, rhs):
        Evidence.__init__(self, rhs)
        self.varName = rhs.varName
        self.value = rhs.value
        
    def getRuleString(self, env={}):
        return 'calculate ' + self.varName + " := " + \
                self._displayFormat(self.name, self.params, env=env)
        
    def getUnifiedString(self):
        return self.varName + " = " + str(self.value)
    
        
class Observation(Evidence):
    
    def __init__(self, rhs):
        Evidence.__init__(self, rhs)
        self.useParams = rhs.useParams
        
    def getRuleString(self, env={}):
        return self._displayFormat(self.name, self.params, env=env)
    
    def getUnifiedString(self):
        #this will use useParams, I imagine
        if self.confidence is None:
            return "Input Data Missing"
        nStr = ""
        if not self.confidence.isTrue():
            nStr = 'not '
        return self._displayFormat(self.name, self.useParams, notStr=nStr)
    
    def getToolTipText(self):
        return self.confidence.applicString()
        

class Simulation(Evidence):
    def __init__(self, sim):
        Evidence.__init__(self, sim)
        self.result = sim.simResult
        
        self.params = self.result.params
        self.guiItem = self.result.guiItem
        
            
    def getRuleString(self, env={}):
        return self.result.getSimName() + self._formatParams()
            
    def getUnifiedString(self):
        return self.result.getDisplayString() + self._formatParams()
    
    def getToolTipText(self):
        return 'found ' + self.confidence.levelString() + ' evidence ' + \
                self.confidence.dirString() + ' ' + self.result.getSimName()
    
    
    @classmethod
    def hasExpansion(cls):
        return True

class Argument(Evidence):
    def __init__(self, arg, params=None):
        self.conclusion = arg.conclusion
        self.params = params
        self.confidence = arg.confidence
        self.evidence = arg.evidence
        self.conflict = arg.conflict
        self.guiItem = None
        #print self.evidence
        
    def getRuleString(self, env={}):
        return 'Argument for ' + self.getConclusionString()    
    
    def __cmp__(self, other):
        if type(other) == type(self):
            if self.confidence is None:
                print 'None confidence wtfbbq!', self.conclusion, self.params
            if self.conflict and not other.conflict:
                return -1
            elif not self.conflict and other.conflict:
                return 1
        return Evidence.__cmp__(self, other)
    
    def getUnifiedString(self):
        #fix this so I do something more useful with my parameters
        #return self.getTitleString()
        #change this back when the rest of the UI is fixed...
        if self.confidence is None:
            return ""
        
        return ((self.conflict and 'Conflicted ' or '') + 'Argument ' + 
                (self.confidence.isTrue() and 'For ' or 'Against ') + 
                self.getConclusionString())
    
    def getTitleString(self):
        return 'Arguments ' + str(self.confidence).replace('CONCLU', self.getConclusionString())
    
    def getConclusionString(self):
        if self.params is not None:
            return self.conclusion.name.title() + self._formatParams()
        else:
            return str(self.conclusion)
        
    def getProEvid(self):
        return [rule for rule in self.evidence if rule.confidence.isTrue()]
    
    def getConEvid(self):
        return [rule for rule in self.evidence if not rule.confidence.isTrue()]
    
    def getAllEvid(self):
        self.evidence.sort(reverse=True)
        return self.evidence
    
    def isValid(self):
        return self.confidence is not None
    
    def setGUIItem(self, guiItem):
        """
        Lets me store the GUI thingy created for this argument so I can get
        it back later
        """
        self.guiItem = guiItem
        
    def getGUIItem(self):
        """
        Get the stored GUI thingy back, or None
        """
        
        return self.guiItem
    
    @classmethod
    def hasExpansion(cls):
        return True

class EvidRule:
    def __init__(self, rule):
        #self.rule = rule
        self.conclusion = rule.conclusion
        self.filledConclusion = rule.filledConclusion
        self.rhsList = [rhs.toEvidence() for rhs in rule.rhsList if rhs.valid()]
        self.confidence = rule.confidence
        self.template = rule.confTemplate
        self.quality = rule.quality
        self.env = self.conclusion.buildEnv(self.filledConclusion)
        
    def getJoinWord(self):
        return self.template.priority and ' and' or ' or'
    
    def getCalcStrings(self):
        return ['- ' + rhs.getRuleString(self.env) for rhs in self.rhsList if rhs.isCalculation()]
    
    def getRealEvidence(self):
        return [rhs.getRuleString(self.env) for rhs in self.rhsList if not rhs.isCalculation()]
        
    def getRuleString(self):
        env = self.conclusion.buildEnv(self.filledConclusion)
        
        joinWord = ' and\n'
        if self.template.priority == False:
            joinWord = ' or\n'
            
        rule = ''.join([rhs.getRuleString(env) + ';\n' for rhs in self.rhsList
                       if rhs.isCalculation()])
            
        rule += joinWord.join([rhs.getRuleString(env) for rhs in self.rhsList
                             if not rhs.isCalculation()]) + ' =>\n   '
        
        if self.template.flip:
            rule += 'not '
            
        rule += str(self.filledConclusion)
        
        return rule
    
    def getUnifiedString(self):
        return self.getRuleString()
    
    def getConclusionString(self):
        return self.confidence.levelString() + ' evidence ' + \
               self.confidence.dirString() + ' ' + str(self.filledConclusion)
               
    def getImplicationString(self):
        conc = ' => '
        if self.template.flip:
            conc += 'not '  
        conc += str(self.filledConclusion)
        
        return conc
        
            
        
    def __cmp__(self, other):
        assert type(self) == type(other)
        return cmp(self.confidence, other.confidence)
    
    def __repr__(self):
        return "; ".join([rhs.getDisplayString() for rhs in self.rhsList])
        

