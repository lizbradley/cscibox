"""
samples.py

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
import pprint

class Sample(object):

    def __init__(self, experiment='input', data={}):
        self.experiment = experiment
        self.data = {experiment:data.copy()}

    def __contains__(self, key):
        return key != 'ALL' and key in self.data.keys

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
        if self.experiment == 'input':
            raise KeyError()
        del self.data[self.experiment][key]

    def has_key(self, key):
        return key in self.data[self.experiment] or key in self.data['input']

    def get(self, experiment, key):
        try:
            return self.data[experiment][key]
        except:
            return None

    def set(self, experiment, key, value):
        self.data.setdefault(experiment, {})
        self.data[experiment][key] = value

    def remove(self, experiment, key):
        if experiment == 'input':
            raise KeyError()
        del self.data[experiment][key]

    def remove_experiment(self, experiment):
        if experiment == 'input':
            raise KeyError()
        del self.data[experiment]

    def experiments(self):
        return sorted(self.data)

    def all_properties(self):
        props = set()
        for experiment, properties in self.data.iteritems():
            props.update(properties)
        return sorted(list(props))

    def properties_for_experiment(self, experiment):
        keys = set(self.data[experiment])
        keys.update(self.data['input'])
        return sorted(list(keys))

    def save(self, path):
        sample_path = os.path.join(path, self.get('input', 'id') + ".txt")
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
        

class VirtualSample(object):

    def __init__(self, sample, experiment):
        self.sample = sample
        self.experiment = experiment

    def __contains__(self, key):
        return key in self.keys()
    def __len__(self):
        return len(self.keys())
    def __iter__(self):
        return iter(self.keys())

    def __getitem__(self, key):
        if key == "experiment":
            return self.experiment
        return self.sample.get(self.experiment, key)
    def __setitem__(self, key, item):
        self.sample.set(self.experiment, key, item)
    def __delitem__(self, key):
        self.sample.remove(self.experiment, key)
        
    def keys(self):
        return self.sample.properties_for_experiment(self.experiment)
        
    def remove_experiment(self):
        if self.experiment != "input":
            self.sample.remove_experiment(self.experiment)


class Samples(object):

    def __init__(self):
        self.samples = {}

    def __len__(self):
        return len(self.samples)

    def __contains__(self, key):
        return key in self.samples

    def add(self, sample):
        self.samples[sample['id']] = sample

    def remove(self, id):
        del self.samples[id]

    def get(self, id):
        return self.samples[id]

    def ids(self):
        return sorted(self.samples)

    def save(self, path):
        samples_path = os.path.join(path, 'samples')

        if not os.path.exists(samples_path):
            os.mkdir(samples_path)
        ids = self.ids()

        # delete samples no longer in self.samples()
        items = os.listdir(samples_path)
        items = [item for item in items if item.endswith('.txt')]
        to_delete = [file for file in items if not file[0:len(file) - 4] in ids]
        for file in to_delete:
            os.remove(os.path.join(samples_path, file))

        # now save all of the current samples to disk
        for id in ids:
            sample = self.get(id)
            sample.save(samples_path)

    def load(self, path):
        print "loading samples"
        samples_path = os.path.join(path, 'samples')

        if not os.path.exists(samples_path):
            os.mkdir(samples_path)

        items = os.listdir(samples_path)
        samples = [item for item in items if item.endswith('.txt')]
        for s in samples:
            sample = Sample()
            sample.load(os.path.join(samples_path, s))
            self.add(sample)
        print "samples loaded"
