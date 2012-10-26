"""
Samples.py

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

from Sample import Sample

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
        return sorted(self.samples.keys())

    def save(self, path):
        samples_path = os.path.join(path, 'samples')

        if not os.path.exists(samples_path):
            os.mkdir(samples_path)

        ids = self.ids()

        # delete samples no longer in self.samples()
        items = os.listdir(samples_path)
        items = [item for item in items if item.endswith('.txt')]
        to_delete = [file for file in items if not file[0:len(file)-4] in ids]
        for file in to_delete:
            os.remove(os.path.join(samples_path, file))

        # now save all of the current samples to disk
        for id in ids:
            sample = self.get(id)
            sample.save(samples_path)

    def load(self, path):
        samples_path =  os.path.join(path, 'samples')

        if not os.path.exists(samples_path):
            os.mkdir(samples_path)

        items   = os.listdir(samples_path)
        samples = [item for item in items if item.endswith('.txt')]
        for s in samples:
            sample = Sample()
            sample.load(os.path.join(samples_path, s))
            self.add(sample)
