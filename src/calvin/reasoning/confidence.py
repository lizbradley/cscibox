"""
confidence.py

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

"""
Confidence Class
A full confidence value is composed of a confidence for and a confidence 
against any given conclusion. Either of these components may be None,
indicating a lack of evidence on that side of the equation. A confidence with 
both sides 'None' is invalid.
Properties
  applic - How applicable something is to the rule, three levels
  valid  - The validity of this confidence, four levels

Member functions
  CmpMag        - Compaires two Confidence's Magnitude
  updateQuality - ???

Static Methods
  getUnifier - Decides whether to andReduce or orReduce
  _orReduce  - Returns the greater Confidence object
  _andReduce - Returns a comination of the minimal Confidence fields
  combine    - The core of the algorithm, sorts a list of confidences,
             * sorts them and reduces the max arguments on each side
"""
class Confidence:
    
    def __init__(self, applic, valid):
        self.applic = applic
        self.valid = valid
        
    def __repr__(self):
        return str(self.applic) + str(self.valid) + " theories"
    
    def dirString(self):
        return self.applic.dirString()
    
    def applicString(self):
        return self.applic.levelString()
    
    def levelString(self):
        return self.applic.levelString() + self.valid.levelString()
    
    """
    More true confidences are larger
    """
    def __cmp__(a, b):
        val = cmp(a.isTrue(), b.isTrue())
        if val == 0:
            val = cmp(a.valid, b.valid)
            if val == 0:
                val = cmp(a.applic, b.applic)
            if not a.isTrue():
                val = -val
        return val
    
    """
    cmpMag()
    This comparison sorts only by magnitude, comparing matches by
    level but not true/false
    """
    def cmpMag(a, b):
        val = cmp(a.valid, b.valid)
        if val == 0:
            val = cmp(a.applic, b.applic)
        return val
        
            
    def __add__(self, val):
        return Confidence(self.applic + val, self.valid)
    
    def __sub__(self, val):
        return Confidence(self.applic - val, self.valid)
    
    def __neg__(self):
        return Confidence(-self.applic, self.valid)
        
    """
    updateQuality()
    ???
    """
    def updateQuality(self, qualTup):
        if self.isTrue():
            self.valid = min(self.valid, qualTup[0])
        else:
            self.valid = min(self.valid, qualTup[1])
        
    def isTrue(self):
        return self.applic.isTrue()
            
    def isStrongly(self, dir):
        if self.valid < Validity.sound:
            return False
        return self.isTrue() == dir
    
    def isProbably(self, dir):
        if self.valid < Validity.prob:
            return False
        return self.isTrue() == dir
    
    def isValid(self):
        return self.match.isValid()
    
    """
    combine()
    So this is in fact where the magic happens, apparently.
    should check around, but given that, here is what I want to do:
    1. sort confidences out into true and false
    2. aggregate from lowest quality to highest. I *think* the right thing to
       do is to take any quality group that has 3 members and bump them
       up a quality level, taking the AVERAGE of the matches. Should make sure
       to use the 'best' evidence group when there are 4+ (and obv multiple
       groups can happen)
    3. having aggregated, take the single max on each side, check for reduction,
       and go along our merry way?
      - but when there are, say, 2 good pros and 1 good con?
      - hey, is this where strong vs. weak comes in?
    
    confidences - A list of confidence objects
    Returns : The top confidence if all confidences are in agreement, or ???
    """
    @staticmethod
    def combine(confidences):
        """
        aggregConfs
        Finds the top two confidences in a list
        confList - A list of confidences
        sortDir  - A boolian that gives the search direction 
        Returns : The top two confidences 
        """
        def aggregConfs(confList, sortDir):
            # These come in sorted.
            if len(confList) == 0:
                return []
            confList.sort(reverse=sortDir)
            
            savedList = confList[:]
            
            # This needs to be done in a slightly better way 
            # If I have 9 plauses I should get a sound, and this doesn't
            # have that ability.
            valList = [
                    Validity.plaus, Validity.prob, Validity.sound,
                    Validity.accept
            ]
            
            for val in valList:
                confs = [conf for conf in confList if conf.valid == val]
                if len(confs) < 3:
                    continue
                
                confList = [conf for conf in confList if conf.valid != val]
                
                for i in xrange(0, len(confs), 3):
                    if len(confs) >= i + 3:
                        confList.append(Confidence(Applic.avg(
                                    [conf.applic for conf in confs[i:i + 3]]),
                                confs[0].valid + 1))

                confList.extend(confs[(len(confs) / 3) * 3:])
                
                confList.sort(reverse=sortDir)
            
            # So now I want to return... the top two, presuming there are 2
            # Make sure this is sorted the right way
            return confList[0:2]
        
        # And then of course there is some more code to fix, 
        # since there are silly assumptions now.
            
        """
        singleCombine()
        Combines two confidences and subtracts confidence if they contradict 
        pos - A confidence ???
        neg - A confidence ???
        Returns : A confidence
        """
        def singleCombine(pos, neg):
            # What is lvl ???
            lvl = pos.applic.cmpLevel(neg.applic)
            baseconf = None

            if pos.valid > neg.valid:
                baseconf = pos
            if pos.valid < neg.valid:
                baseconf = neg
                lvl = -lvl

            # If one is greater, return the greater one or ???
            if baseconf:
                if pos.valid.outScale(neg.valid) or lvl == 2:
                    return baseconf
                else:
                    napp = baseconf.applic
                    nval = baseconf.valid
                    if lvl < 0:
                        nval = nval - 1
                       # print baseconf.valid, nval
                    else:
                        napp = napp - 1
                    return Confidence(napp, nval)

            # Else if pos.valid == neg.valid
            else: 
                if lvl == 1:
                    return Confidence(pos.applic - 1, pos.valid - 1)
                elif lvl == 2:
                    return Confidence(pos.applic - 1, pos.valid)
                elif lvl < 0:
                    return Confidence(neg.applic - pos.applic.level, neg.valid)
                # pos.applic = neg.applic
                else: 
                    nval = neg.valid - 2
                    napp = neg.applic - 1
                    if neg.valid < Validity.sound:
                        napp -= 1
                    return Confidence(napp, nval)
             
        # End function definitions ###########################################
        assert len(confidences) > 0
        
        # Step 1: split and aggregate
        topPos = aggregConfs([con for con in confidences if con.isTrue()],
                             True)
        topNeg = aggregConfs([con for con in confidences if not con.isTrue()],
                             False)
        
        if len(topPos) == 0:
            return topNeg[0]
        elif len(topNeg) == 0:
            return topPos[0]
        elif len(topPos) == len(topNeg):
            first = singleCombine(topPos[0], topNeg[0])
            if len(topPos) > 1:
                second = singleCombine(topPos[1], topNeg[1])
                if first.isTrue() and not second.isTrue():
                    return singleCombine(first, second)
                elif second.isTrue() and not first.isTrue():
                    return singleCombine(second, first)
            return first
        else:
            first = singleCombine(topPos[0], topNeg[0])
            if len(topNeg) == 2: #pos will be 1
                if first.isTrue():
                    return singleCombine(first, topNeg[1])
            else:
                if not first.isTrue():
                    return singleCombine(topPos[1], first)
                
            return first
        
        print "this can't happen"
        return Confidence(Applic.ft, Validity.plaus)
        
    """
    _andReduce 
    Reduces two confidences to the minimum aplicability and the minimal
    validity
    a - A Confidence object
    b - A Confidence object
    Returns :  A confidence object that takes the minimum of both fields
    """
    @staticmethod
    def _andReduce(a, b):
        return Confidence(min(a.applic, b.applic), min(a.valid, b.valid))
    
    """
    _orReduce
    Returns the greater confidence
    a - A confidence object
    b - A confidence object
    Returns : A confidence object
    """
    @staticmethod
    def _orReduce(a, b):
        if a.applic > b.applic:
            return Confidence(a.applic, a.valid)
        elif a.applic < b.applic:
            return Confidence(b.applic, b.valid)
        
        return Confidence(a.applic, max(a.valid, b.valid))
    
    """
    getUnifier
    Desideds whether to orReduce or andReduce
    priority - A boolean
    Returns : If priority is true andReduce else orReduce
    """
    @staticmethod
    def getUnifier(priority):
        if priority:
            return Confidence._andReduce
        else:
            return Confidence._orReduce

    
    
"""
Confidence Class
Confidence template class stores the options available to rules for internal
confidence unification and performs said unification for said rules
Properties
  increment - An integer of how much to change a match value
  flip      - A boolean on whether to flip or not
  priority  - A boolean on whether true or false takes a priority

Members functions
  unify - Unifies all the confidence into a single confidence
"""
class Template:
    
    """
    __init__
    Constructor takes the following parameters:
    
    increment: whether and how much to change the "Match" value for the 
               rule (default = 0)

    flip: whether to flip the value for the rule the other direction from 
          the evidence (default = False)
          
    priority: whether "True" or "False" values take priority. 
              More specifically, whether the minimum or maximum confidence
              from the individual items is taken, when more than
              one item exists (default = False = min)
              
    These are applied in the order:
    Select one confidence based on priority
    Flip if appropriate
    Increment
    """
    def __init__(self, increment=0, flip=False, priority=False):
        self.increment = increment
        self.flip = flip
        self.priority = priority
        
    """
    unify
    Turns the set of confs in the rhses into a single conf for the whole rule.
    quality - The quality of this rule???
    confs   - The lists of confidences that we want to compress
    Returns : A compressed confidence
    """
    def unify(self, quality, confs):
        # Filter out Nones
        confs = [conf for conf in confs if conf] 
        
        if len(confs) > 0:
            conf = reduce(Confidence.getUnifier(self.priority), confs)
            #reduce doesn't copy the confidence when there's only one and
            #things get overwritten, so this hack prevents that by forcing
            #a copy.
            conf = Confidence(conf.applic, conf.valid)
        else:
            conf = Confidence(Applic.nil, Validity.plaus)
        
        if type(quality) != types.TupleType:
            quality = (quality, quality)
                
        conf.updateQuality(quality)
            
        if self.flip:
            conf = -conf
        
        conf = conf + self.increment
        return conf
        
"""
Applic Class
Stores the direction and extremity of a "match" to a rule.
Matches can be falsified, compared, and simple addition can be performed
on them (Match + 1 makes a Match one more step toward true,
assuming it is not already at the max).

This is an super important class that captures whether or not a confidence
rule is applicable, and how applicable
"""
class Applic:
    
    @staticmethod
    def avg(lis):
        return Applic._Applic.avg(lis)
        
    class _Applic:
        """
        internal "Match" class to hide the constructor for Match objects
        """
        
        levels = {0:"", 1:"partly", 2:"mostly", 3:"highly"}
        dirs = {None:"", True:"for", False:"against"}
        
        def __init__(self, level, direction):
            self.level = level
            self.dir = direction
            
        def __repr__(self):
            return Applic._Applic.dirs[self.dir] + ' CONCLU using ' + \
                   Applic._Applic.levels[self.level] + ' applicable '
                   
        def dirString(self):
            return Applic._Applic.dirs[self.dir]
        
        def levelString(self):
            return Applic._Applic.levels[self.level] + ' applicable '
        
        def __cmp__(self, other):
            """
            More true matches are LARGER
            """
            assert type(self) == type(other)
            tf = cmp(self.dir, other.dir)
            if tf == 0:
                return cmp(self.level, other.level)
            else:
                return tf
            
        def cmpLevel(self, other):
            """
            compare just the levels; give a mildly useful answer here.
            (range from -2 to 2)
            """
            assert type(self) == type(other)
            return self.level - other.level
            
        
        #add and sub make any match more or less extreme. This may turn out to be wrong later
        def __add__(self, val):
            return Applic._Applic(self.__snap(self.level + val), self.dir)
        
        def __sub__(self, val):
            return Applic._Applic(self.__snap(self.level - val), self.dir)
        
        def __neg__(self):
            return Applic._Applic(self.level, not self.dir)
            
        def __snap(self, val):
            if val < 1:
                return 1
            elif val > 3:
                return 3
            else:
                return val
        
        def isValid(self):
            return self.level != 0
        
        def isTrue(self):
            return self.dir
            
        def getLevel(self):
            return self.level
        
        @staticmethod
        def avg(lis):
            """
            Average some number of applicabilities.
            Assumes all truths are the same
            """
            val = sum([app.level for app in lis]) / len(lis)
            return Applic._Applic(val, lis[0].dir) - 1
            
                
    dt = _Applic(1, True)
    ft = _Applic(2, True)
    ct = _Applic(3, True)
    df = _Applic(1, False)
    ff = _Applic(2, False)
    cf = _Applic(3, False)
    
    nil = _Applic(0, None)
    
    RANKS = 6 # don't actually show 'nil' matches
    
        
"""
Validity Class
Stores a quality judgement of knowledge. For a rule, this is the quality
of the rule. For a derived conclusion, this is the lowest quality of any
piece of knowledge used in deriving the conclusion. Arithmetic operations
and comparisons are available.

This is a super important class that represents how valid an confidence is
"""
class Validity:
    
    @staticmethod
    def getValidity(rank):
        return Validity._Validity.getValidity(rank)
        
    
    class _Validity:
        """
        internal "Quality" class to hide the constructor for Quality objects
        """
        
        levels = {0:"plausible", 1:"probable", 2:"sound", 3:"accepted"}
        
        def __init__(self, level):
            self.qual = level
            
        @staticmethod
        def getValidity(rank):
            #Validity._Validity.
            return Validity._Validity(Validity._Validity.__snap(rank))
            
        def __repr__(self):
            return Validity._Validity.levels[self.qual]
        
        def levelString(self):
            return Validity._Validity.levels[self.qual]
        
        def __cmp__(self, other):
            assert type(other) == type(self)
            return cmp(self.qual, other.qual)
        
        def __add__(self, val):
            return Validity._Validity(self.__snap(self.qual + val))
        
        def __sub__(self, val):
            return Validity._Validity(self.__snap(self.qual - val))
        
        @staticmethod
        def __snap(val):
            if val < 0:
                return 0
            elif val > 3:
                return 3
            else:
                return val
            
        def outScale(self, other):
            assert type(self) == type(other)
            return abs(self.qual - other.qual) > 1
            
    plaus = _Validity(0)
    prob = _Validity(1)
    sound = _Validity(2)
    accept = _Validity(3)
    
    RANKS = 4
    
    




