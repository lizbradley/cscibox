"""
Factors.py

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

import os
import os.path

from ACE.Framework import Factor

class Factors(object):

    def __init__(self):
        self.factors = {}

    def __str__(self):
        return '{factors : %s}' % (self.factors)

    __repr__ = __str__

    def add(self, factor):
        self.factors[factor.get_name()] = factor

    def remove(self, name):
        del self.factors[name]

    def get(self, name):
        return self.factors[name]

    def names(self):
        keys = self.factors.keys()
        keys.sort()
        return keys

    def save(self, path):
        factors_path =  os.path.join(path, "factors")

        if not os.path.exists(factors_path):
            os.mkdir(factors_path)

        keys = self.names()

        # delete factors no longer in self.factors()
        items = os.listdir(factors_path)
        to_delete = [file for file in items if not file[0:len(file)-4] in keys]
        for file in to_delete:
            # skip invisible Unix directories like ".svn"
            if file.startswith("."):
                continue
            os.remove(os.path.join(factors_path, file))

        for name in keys:
            factor = self.get(name)
            factor.save(factors_path)

    def load(self, path):
        factors_path =  os.path.join(path, "factors")

        if not os.path.exists(factors_path):
            os.mkdir(factors_path)

        items   = os.listdir(factors_path)
        factors = [item for item in items if item.endswith('.txt')]
        for name in factors:
            factor = Factor(name[0:len(name)-4])
            factor.load(os.path.join(factors_path, name))
            self.add(factor)

if __name__ == '__main__':
    f = Factors()
    f.load('.')
    names = f.names()
    for name in names:
        factor = f.get(name)
        print "%s:" % (factor.get_name())
        modes = factor.get_mode_names()
        for mode in modes:
            print "\t%s" % (mode)
            comps = factor.get_components_for_mode(mode)
            for comp in comps:
                print "\t\t%s" % (comp)
    f.save('.')
