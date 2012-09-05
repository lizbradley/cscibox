"""
Sample.py

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
import pprint

class Sample(object):

    nuclide_independent = []
    nuclide_independent.append('default lapse rate')
    nuclide_independent.append('default sea-level pressure')
    nuclide_independent.append('default sea-level temperature')
    nuclide_independent.append('density')
    nuclide_independent.append('elevation')
    nuclide_independent.append('id')
    nuclide_independent.append('independent age')
    nuclide_independent.append('independent age uncertainty')
    nuclide_independent.append('landform group')
    nuclide_independent.append('latitude')
    nuclide_independent.append('longitude')
    nuclide_independent.append('shielding factor')
    nuclide_independent.append('vertical movement')

    def __init__(self):
        self.nuclide    = 'ALL'
        self.experiment = 'input'
        self.data = {}
        self.data[self.nuclide] = {}
        self.data[self.nuclide][self.experiment] = {}

    def __contains__(self, key):
        keys = self.data.keys()
        keys.remove('ALL')
        return key in keys

    def __getitem__(self, key):
        try:
            return self.data[self.nuclide][self.experiment][key]
        except KeyError:
            try:
                return self.data[self.nuclide]['input'][key]
            except KeyError:
                try:
                    return self.data['ALL']['input'][key]
                except KeyError:
                    #print "Returning None for Sample %s for Key %s" % (self.data['ALL']['input']['id'], key)
                    return None

    def __setitem__(self, key, item):
        if key in Sample.nuclide_independent:
            self.data['ALL']['input'][key] = item
            return
        if self.nuclide not in self.data:
            self.data[self.nuclide] = {}
        if self.experiment not in self.data[self.nuclide]:
            self.data[self.nuclide][self.experiment] = {}
        self.data[self.nuclide][self.experiment][key] = item

    def __delitem__(self, key):
        assert self.experiment != 'input'
        del self.data[self.nuclide][self.experiment][key]

    def get_current_nuclide(self):
        return self.nuclide

    def get_current_experiment(self):
        return self.experiment

    def has_key(self, key):
        present = key in self.data[self.nuclide][self.experiment]
        if not present:
            present = key in self.data[self.nuclide]['input']
            if not present:
                present = key in self.data['ALL']['input']
        return present

    def set_experiment(self, experiment):
        self.experiment = experiment

    def set_nuclide(self, nuclide):
        self.nuclide = nuclide

    def get(self, nuclide, experiment, key):
        try:
            return self.data[nuclide][experiment][key]
        except:
            #print "Returning None for Sample %s for Key %s" % (self.data['ALL']['input']['id'], key)
            return None

    def set(self, nuclide, experiment, key, value):
        if nuclide not in self.data:
            self.data[nuclide] = {}
        if experiment not in self.data[nuclide]:
            self.data[nuclide][experiment] = {}
        self.data[nuclide][experiment][key] = value

    def remove(self, nuclide, experiment, key):
        assert experiment != 'input'
        del self.data[nuclide][experiment][key]

    def remove_experiment(self, nuclide, experiment):
        assert experiment != 'input'
        del self.data[nuclide][experiment]

    def nuclides(self):
        keys = self.data.keys()
        keys.remove('ALL')
        return sorted(keys)

    def experiments(self, nuclide):
        return sorted(self.data[nuclide].keys())

    def all_properties(self):
        props = []
        for nuclide in self.nuclides():
            for experiment in self.experiments(nuclide):
                if experiment == "input":
                    continue
                props.extend(self.properties_for_experiment(nuclide,experiment))
        no_dups = set(props)
        return sorted(list(no_dups))

    def properties_for_experiment(self, nuclide, experiment):
        keys = self.data[nuclide][experiment].keys()
        keys.extend(self.data[nuclide]['input'])
        keys.extend(self.data['ALL']['input'])
        no_dups = set(keys)
        keys = list(no_dups)
        return sorted(keys)

    def save(self, path):
        sample_path = os.path.join(path, self.get('ALL','input','id') + ".txt")
        f = open(sample_path, "w")
        f.write(pprint.pformat(self.data))
        f.flush()
        f.close()

    def load(self, file):
        f = open(file, "U")
        data = f.read()
        f.close()
        self.data = eval(data)
        self.nuclide = 'ALL'
        self.experiment = 'input'
