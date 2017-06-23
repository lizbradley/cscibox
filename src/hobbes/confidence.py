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
import logging

class Confidence(object):
    """
    A full confidence value is composed of a confidence for and a confidence
    against any given conclusion. Either of these components may be None,
    indicating a lack of evidence on that side of the equation. A confidence with
    both sides 'None' is invalid.
    Properties
      applic - How applicable something is to the rule, three levels
      valid  - The validity of this confidence, four levels
    """

    def __init__(self, applic, valid):
        self.applic = applic
        self.valid = valid
        self.logger = logging.getLogger(__name__)

    def __repr__(self):
        return str(self.applic) + str(self.valid)
    
    def __cmp__(a, b):
        """
        More-true confidences are larger
        """
        val = cmp(a.is_true(), b.is_true())
        if val == 0:
            val = cmp(a.valid, b.valid)
            if val == 0:
                val = cmp(a.applic, b.applic)
            if not a.is_true():
                val = -val
        return val

    def cmp_mag(a, b):
        """
        This comparison sorts only by magnitude, comparing matches by
        level but not true/false
        """
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

    def update_validity(self, valtup):
        if self.is_true():
            self.valid = min(self.valid, valtup[0])
        else:
            self.valid = min(self.valid, valtup[1])

    def is_true(self):
        return self.applic.is_true()

    def is_strongly(self, dir):
        if self.valid < Validity.sound:
            return False
        return self.is_true() == dir

    def is_probably(self, dir):
        if self.valid < Validity.prob:
            return False
        return self.is_true() == dir

    def is_valid(self):
        return self.match.is_valid()
    
    @staticmethod
    def combine(confidences):
        """
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
        
        def aggreg_confs(confList, sortDir):
            """
            Finds the top two confidences in a list
            confList - A list of confidences
            sortDir  - A boolian that gives the search direction
            Returns : The top two confidences
            """
            # These come in sorted.
            if len(confList) == 0:
                return []
            confList.sort(reverse=sortDir)

            savedList = confList[:]

            # This needs to be done in a slightly better way
            # If I have 9 plauses I should get a sound, and this doesn't
            # have that ability.
            valList = [Validity.plausible, Validity.probable, 
                       Validity.sound, Validity.accepted]

            for val in valList:
                confs = [conf for conf in confList if conf.valid == val]
                if len(confs) < 3:
                    continue

                confList = [conf for conf in confList if conf.valid != val]

                for i in xrange(0, len(confs), 3):
                    if len(confs) >= i + 3:
                        confList.append(Confidence(Applicability.avg(
                                    [conf.applic for conf in confs[i:i + 3]]),
                                confs[0].valid + 1))

                confList.extend(confs[(len(confs) / 3) * 3:])

                confList.sort(reverse=sortDir)

            # So now I want to return... the top two, presuming there are 2
            # Make sure this is sorted the right way
            return confList[0:2]

        # And then of course there is some more code to fix,
        # since there are silly assumptions now.

        def single_combine(pos, neg):
            """
            Combines two confidences and subtracts confidence if they contradict
            pos - the confidence in favor of a conclusion
            neg - the confidence against a conclusion
            Returns : A confidence
            """
            lvl = pos.applic.cmp_lvl(neg.applic)
            baseconf = None

            if pos.valid > neg.valid:
                baseconf = pos
            if pos.valid < neg.valid:
                baseconf = neg
                lvl = -lvl

            # If one is greater, return the greater one or ???
            if baseconf:
                if pos.valid.outscale(neg.valid) or lvl == 2:
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
        topPos = aggreg_confs([con for con in confidences if con.is_true()],
                             True)
        topNeg = aggreg_confs([con for con in confidences if not con.is_true()],
                             False)

        if len(topPos) == 0:
            return topNeg[0]
        elif len(topNeg) == 0:
            return topPos[0]
        elif len(topPos) == len(topNeg):
            first = single_combine(topPos[0], topNeg[0])
            if len(topPos) > 1:
                second = single_combine(topPos[1], topNeg[1])
                if first.is_true() and not second.is_true():
                    return single_combine(first, second)
                elif second.is_true() and not first.is_true():
                    return single_combine(second, first)
            return first
        else:
            first = single_combine(topPos[0], topNeg[0])
            if len(topNeg) == 2: #pos will be 1
                if first.is_true():
                    return single_combine(first, topNeg[1])
            else:
                if not first.is_true():
                    return single_combine(topPos[1], first)

            return first

        self.logger.warning("this can't happen")
        return Confidence(Applicability.partlyfor, Validity.plausible)

    
    @staticmethod
    def _and_reduce(a, b):
        """
        Reduces two confidences to the minimum applicability and the minimal
        validity
        Returns :  A confidence object that takes the minimum of both fields
        """
        return Confidence(min(a.applic, b.applic), min(a.valid, b.valid))

    @staticmethod
    def _or_reduce(a, b):
        """
        Returns the greater confidence
        Returns : A confidence object
        """
        if a.applic > b.applic:
            return Confidence(a.applic, a.valid)
        elif a.applic < b.applic:
            return Confidence(b.applic, b.valid)

        return Confidence(a.applic, max(a.valid, b.valid))

    
    @staticmethod
    def get_unifier(priority):
        """
        Decides whether to orReduce or andReduce
        Returns : If priority is true andReduce else orReduce
        """
        if priority:
            return Confidence._and_reduce
        else:
            return Confidence._or_reduce

class Template(object):
    """
    Confidence template class stores the options available to rules for internal
    confidence unification and performs said unification for said rules
    """
    
    def __init__(self, flip=False, priority=True, increment=0):
        """
        Constructor takes the following parameters:
    
        increment: whether and how much to change the "Match" value for the
                   rule (default = 0)
    
        flip: whether to flip the value for the rule the other direction from
              the evidence (default = False)
    
        priority: whether "True" or "False" values take priority.
                  More specifically, whether the rule is an 'AND' or an 'OR'
                  rule (priority = False for 'OR')
    
        These are applied in the order:
        Select one confidence based on priority
        Flip if appropriate
        Increment
        """
        self.increment = increment
        self.flip = flip
        self.priority = priority

    
    def unify(self, quality, confs):
        """
        Turns the set of confs in the rhses into a single conf for the whole rule.
        quality - The quality of this rule
        confs   - The lists of confidences that we want to compress
        Returns : A compressed confidence
        """
        # Filter out Nones
        confs = [conf for conf in confs if conf]

        if len(confs) > 0:
            conf = reduce(Confidence.get_unifier(self.priority), confs)
            #reduce doesn't copy the confidence when there's only one and
            #things get overwritten, so this hack prevents that by forcing
            #a copy.
            conf = Confidence(conf.applic, conf.valid)
        else:
            conf = Confidence(Applicability.nil, Validity.plausible)

        if type(quality) != types.TupleType:
            quality = (quality, quality)

        conf.update_validity(quality)

        if self.flip:
            conf = -conf

        conf = conf + self.increment
        return conf


class Applicability(object):
    """
    Applicability Class
    Stores the direction and extremity of a "match" to a rule.
    Matches can be falsified, compared, and simple addition can be performed
    on them (Match + 1 makes a Match one more step toward true,
    assuming it is not already at the max).
    
    This is a super important class that captures whether or not a confidence
    rule is applicable, and how applicable
    """

    @staticmethod
    def avg(lis):
        return Applicability._Applic.avg(lis)

    class _Applic(object):
        """
        internal "Match" class to hide the constructor for Match objects
        """

        levels = {0:"", 1:"partly", 2:"mostly", 3:"highly"}
        dirs = {None:"NIL", True:"FOR", False:"AGAINST"}

        def __init__(self, level, direction):
            self.level = level
            self.dir = direction

        def __repr__(self):
            return Applicability._Applic.dirs[self.dir] + ' CONCLU (' + \
                   Applicability._Applic.levels[self.level] + ' applicable '

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

        def cmp_lvl(self, other):
            """
            compare just the levels; give a mildly useful answer here.
            (range from -2 to 2)
            """
            assert type(self) == type(other)
            return self.level - other.level


        #add and sub make any match more or less extreme. This may turn out to be wrong later
        def __add__(self, val):
            return Applicability._Applic(self.__snap(self.level + val), self.dir)

        def __sub__(self, val):
            return Applicability._Applic(self.__snap(self.level - val), self.dir)

        def __neg__(self):
            return Applicability._Applic(self.level, not self.dir)

        def __snap(self, val):
            if val < 1:
                return 1
            elif val > 3:
                return 3
            else:
                return val

        def is_valid(self):
            return self.level != 0

        def is_true(self):
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
            return Applicability._Applic(val, lis[0].dir) - 1


    partlyfor = _Applic(1, True)
    mostlyfor = _Applic(2, True)
    highlyfor = _Applic(3, True)
    partlyagainst = _Applic(1, False)
    mostlyagainst = _Applic(2, False)
    highlyagainst = _Applic(3, False)

    weaklyfor = partlyfor
    weaklyagainst = partlyagainst

    nil = _Applic(0, None)

    RANKS = 6 # don't actually show 'nil' matches



class Validity(object):
    """
    Validity Class
    Stores a quality judgement of knowledge. For a rule, this is the quality
    of the rule. For a derived conclusion, this is the lowest quality of any
    piece of knowledge used in deriving the conclusion. Arithmetic operations
    and comparisons are available.
    
    This is a super important class that represents how valid a confidence is
    """
    
    class _Validity(object):
        """
        internal "Validity" class to hide the constructor for Quality objects
        """

        levels = {0:"plausible", 1:"probable", 2:"sound", 3:"accepted"}

        def __init__(self, level):
            self.qual = level

        def __repr__(self):
            return Validity._Validity.levels[self.qual] + ')'

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

        def outscale(self, other):
            assert type(self) == type(other)
            return abs(self.qual - other.qual) > 1

    plausible = _Validity(0)
    probable = _Validity(1)
    sound = _Validity(2)
    accepted = _Validity(3)

    RANKS = 4






