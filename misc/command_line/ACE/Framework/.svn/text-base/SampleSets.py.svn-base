import os
import os.path

from ACE.Framework import SampleSet

class SampleSets(object):

    def __init__(self):
        self.sets = {}

    def __str__(self):
        return '%s' % (self.sets)

    __repr__ = __str__

    def add(self, set):
        self.sets[set.get_name()] = set

    def remove(self, name):
        del(self.sets[name])

    def get(self, name):
        return self.sets[name]

    def names(self):
        keys = self.sets.keys()
        keys.sort()
        return keys

    def save(self, path):
        sets_path =  os.path.join(path, 'sets')

        if not os.path.exists(sets_path):
            os.mkdir(sets_path)

        set_names = self.names()

        # delete sample sets no longer in self.sets()
        items = os.listdir(sets_path)
        to_delete = [dir for dir in items if not dir in set_names]
        for dir in to_delete:
            # skip invisible Unix directories like ".svn"
            if dir.startswith("."):
                continue
            dir_path = os.path.join(sets_path, dir)
            # since each item is a directory, we need to
            # remove all files in the directory before
            # we can delete it.
            items = os.listdir(dir_path)
            for file in items:
                os.remove(os.path.join(dir_path, file))
            os.rmdir(dir_path)

        for name in set_names:
            sample_set = self.get(name)
            sample_set.save(sets_path)

    def load(self, path):
        sets_path =  os.path.join(path, 'sets')

        if not os.path.exists(sets_path):
            os.mkdir(sets_path)

        items = os.listdir(sets_path)
        dirs  = [item for item in items if os.path.isdir(os.path.join(sets_path, item))]
        for dir in dirs:
            # skip invisible Unix directories like ".svn"
            if dir.startswith("."):
                continue
            sample_set = SampleSet(dir)
            sample_set.load(os.path.join(sets_path, dir))
            self.add(sample_set)
