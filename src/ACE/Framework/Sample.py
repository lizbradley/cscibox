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

    def __init__(self, experiment='input', data={}):
        self.experiment = experiment
        self.data = {experiment:data.copy()}

    def __contains__(self, key):
        keys = self.data.keys()
        keys.remove('ALL')
        return key in keys

    def __getitem__(self, key):
        try:
            return self.data[self.experiment][key]
        except KeyError:
            try:
                return self.data['input'][key]
            except KeyError:
                return None

    def __setitem__(self, key, item):
        self.data[self.experiment][key] = item

    def __delitem__(self, key):
        assert self.experiment != 'input'
        del self.data[self.experiment][key]

    def get_current_experiment(self):
        return self.experiment

    def has_key(self, key):
        return key in self.data[self.experiment] or key in self.data['input']

    def set_experiment(self, experiment):
        self.experiment = experiment

    def get(self, experiment, key):
        try:
            return self.data[experiment][key]
        except:
            return None

    def set(self, experiment, key, value):
        self.data.setdefault(experiment, {})
        self.data[experiment][key] = value

    def remove(self, experiment, key):
        assert experiment != 'input'
        del self.data[experiment][key]

    def remove_experiment(self, experiment):
        assert experiment != 'input'
        del self.data[experiment]

    def experiments(self):
        return sorted(self.data.keys())

    def all_properties(self):
        props = set()
        for experiment in self.data:
            if experiment == "input":
                continue
            props.update(self.properties_for_experiment(experiment))
        return sorted(list(props))

    def properties_for_experiment(self, experiment):
        keys = set(self.data[experiment].keys())
        keys.update(self.data['input'].keys())
        return sorted(list(keys))

    def save(self, path):
        sample_path = os.path.join(path, self.get('input','id') + ".txt")
        f = open(sample_path, "w")
        f.write(pprint.pformat(self.data))
        f.flush()
        f.close()

    def load(self, file):
        f = open(file, "U")
        data = f.read()
        f.close()
        self.data = eval(data)
        self.experiment = 'input'
