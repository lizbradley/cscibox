import os
import os.path

from ACE.Framework.Experiment import Experiment

class Experiments(object):

    def __init__(self):
        self.experiments = {}

    def __str__(self):
        return '{experiments : %s}' % (self.experiments)

    __repr__ = __str__

    def add(self, experiment):
        self.experiments[experiment['name']] = experiment

    def remove(self, name):
        del self.experiments[name]

    def get(self, name):
        return self.experiments[name]

    def names(self):
        keys = self.experiments.keys()
        keys.sort()
        return keys

    def save(self, path):
        experiments_path =  os.path.join(path, "experiments")

        if not os.path.exists(experiments_path):
            os.mkdir(experiments_path)

        keys = self.names()

        # delete experiments no longer in self.experiments()
        items = os.listdir(experiments_path)
        to_delete = [file for file in items if not file[0:len(file)-4] in keys]
        for file in to_delete:
            os.remove(os.path.join(experiments_path, file))

        for name in keys:
            experiment = self.get(name)
            experiment.save(experiments_path)

    def load(self, path):
        experiments_path =  os.path.join(path, "experiments")

        if not os.path.exists(experiments_path):
            os.mkdir(experiments_path)

        items   = os.listdir(experiments_path)
        experiments = [item for item in items if item.endswith('.txt')]
        for name in experiments:
            experiment = Experiment(name[0:len(name)-4])
            experiment.load(os.path.join(experiments_path, name))
            self.add(experiment)
