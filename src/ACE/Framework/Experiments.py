"""
experiments.py

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


class Experiment(object):

    def __init__(self, name):
        self.atts = {'name':name}

    def __len__(self):
        return len(self.atts)
        
    def __contains__(self, key):
        return key in self.atts

    def __getitem__(self, key):
        return self.atts[key]

    def __setitem__(self, key, item):
        self.atts[key] = item

    def __delitem__(self, key):
        del self.atts[key]

    def keys(self):
        return self.atts.keys()

    def report(self):
        maxlen = max(self.atts, len)
        #sort names, forcing "name" to the top of the list
        names = sorted(self.atts, lambda a,b: a == 'name' and -1 or 
                                    (b == 'name' and 1 or cmp(a, b)))
        buf = '\n'.join([' : '.join((name.ljust(maxlen), 
                                     str(self.atts[name]))) 
                         for name in names])
        return buf + '\n'

    def save(self, path):
        exp_path = os.path.join(path, self["name"] + ".txt")
        f = open(exp_path, "w")
        f.write(repr(self.atts))
        f.write(os.linesep)
        f.flush()
        f.close()

    def load(self, fName):
        f = open(fName, "U")
        self.atts = eval(f.readline().strip())
        f.close()

class Experiments(object):

    def __init__(self):
        self.experiments = {}

    def __str__(self):
        return '{experiments : %s}' % (self.experiments)
    def __repr__(self):
        return repr(self.experiments)

    def add(self, experiment):
        self.experiments[experiment['name']] = experiment

    def remove(self, name):
        del self.experiments[name]

    def get(self, name):
        return self.experiments[name]

    def names(self):
        return sorted(self.experiments)

    def save(self, path):
        experiments_path = os.path.join(path, "experiments")
        if not os.path.exists(experiments_path):
            os.mkdir(experiments_path)

        keys = self.names()

        # delete experiments no longer in self.experiments()
        items = os.listdir(experiments_path)
        to_delete = [file for file in items if not file[0:len(file) - 4] in keys]
        for file in to_delete:
            # skip invisible Unix directories like ".svn"
            if file.startswith("."):
                continue
            os.remove(os.path.join(experiments_path, file))

        for name in keys:
            experiment = self.get(name)
            experiment.save(experiments_path)

    def load(self, path):
        experiments_path = os.path.join(path, "experiments")

        if not os.path.exists(experiments_path):
            os.mkdir(experiments_path)

        items = os.listdir(experiments_path)
        experiments = [item for item in items if item.endswith('.txt')]
        for name in experiments:
            experiment = Experiment(name[0:len(name) - 4])
            experiment.load(os.path.join(experiments_path, name))
            self.add(experiment)
