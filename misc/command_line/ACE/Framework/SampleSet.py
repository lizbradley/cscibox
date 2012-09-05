import os
import os.path

from ACE.Framework.Sample import Sample

class SampleSet(object):

    def __init__(self, name):
        self.name    = name
        self.samples = {}
        self.nuclide = None

    def __str__(self):
        return '{name : %s, samples : %s}' % (self.name, self.samples)

    __repr__ = __str__

    def add(self, sample):
        id = sample.get("input", "id")
        if id != None:
            self.samples[id] = sample

    def remove(self, id):
        del(self.samples[id])

    def get(self, id):
        return self.samples[id]

    def get_name(self):
        return self.name

    def get_nuclide(self):
        return self.nuclide

    def ids(self):
        keys = self.samples.keys()
        keys.sort()
        return keys

    def size(self):
        return len(self.samples)

    def save(self, path):
        set_path =  os.path.join(path, self.name)

        if not os.path.exists(set_path):
            os.mkdir(set_path)

        keys = self.ids()

        # delete samples no longer in self.samples()
        items = os.listdir(set_path)
        to_delete = [file for file in items if not file[0:len(file)-4] in keys]
        for file in to_delete:
            os.remove(os.path.join(set_path, file))

        for id in keys:
            sample = self.get(id)
            sample.save(set_path)

    def load(self, path):
        items   = os.listdir(path)
        samples = [item for item in items if item.endswith('.txt')]
        for s in samples:
            sample = Sample()
            sample.load(os.path.join(path, s))
            self.add(sample)
        self.nuclide = self.samples.values()[0]['nuclide']
