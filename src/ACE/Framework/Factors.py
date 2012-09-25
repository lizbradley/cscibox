"""
factors.py

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

import os.path

class Factor(object):

    """A factor in ACE is a placeholder within workflows that allow
       different components to be plugged into a workflow depending
       on the 'mode' of the factor.

       Operationally, an experiment allows a user to specify the
       different modes for all factors contained within a particular
       workflow. Each mode is associated with a different component.
       Once an experiment's factor modes have all been specified, the
       workflow object creates a workflow that plugs in the correct
       component for each factor."""

    def __init__(self, name):
        self.name = name
        self.modes = {}

    def __str__(self):
        return '{name : %s, modes : %s}' % (self.name, self.modes)
    def __repr__(self):
        return repr(self.modes)

    def add_mode(self, name, components):
        """add_mode creates a new mode with the specified name.
           components is a list of component names, typically
           consisting of just one name. If multiple names are
           listed, the factor will instantiate multiple
           components for a workflow and hook the components
           together in the order specified by the list."""
        self.modes[name] = components

    def get_components_for_mode(self, name):
        return self.modes[name]

    def get_mode_names(self):
        return sorted(self.modes)

    def get_name(self):
        return self.name

    def remove_mode(self, name):
        del self.modes[name]

    def save(self, path):
        factor_path = os.path.join(path, self.name + ".txt")
        f = open(factor_path, "w")
        for mode in self.get_mode_names():
            components = self.get_components_for_mode(mode)
            f.write(mode)
            f.write(" : ")
            f.write(repr(components))
            f.write(os.linesep)
        f.flush()
        f.close()

    def load(self, file):
        f = open(file, "U")
        
        lines = f.readlines()

        f.close()

        lines = [line.strip() for line in lines]
        lines = [line for line in lines if line != '']
        
        for line in lines:
            index = line.find(":")
            mode = line[0:index - 1]
            comps = line[index + 2:]
            self.add_mode(mode, eval(comps))
        f.close()


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
        factors_path = os.path.join(path, "factors")
        if not os.path.exists(factors_path):
            os.mkdir(factors_path)

        keys = self.names()

        # delete factors no longer in self.factors()
        items = os.listdir(factors_path)
        to_delete = [file for file in items if not file[0:len(file) - 4] in keys]
        for file in to_delete:
            # skip invisible Unix directories like ".svn"
            if file.startswith("."):
                continue
            os.remove(os.path.join(factors_path, file))

        for name in keys:
            factor = self.get(name)
            factor.save(factors_path)

    def load(self, path):
        factors_path = os.path.join(path, "factors")
        if not os.path.exists(factors_path):
            os.mkdir(factors_path)

        items = os.listdir(factors_path)
        factors = [item for item in items if item.endswith('.txt')]
        for name in factors:
            factor = Factor(name[0:len(name) - 4])
            factor.load(os.path.join(factors_path, name))
            self.add(factor)

