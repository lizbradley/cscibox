import os
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
        self.name  = name
        self.modes = {}

    def __str__(self):
        return '{name : %s, modes : %s}' % (self.name, self.modes)

    __repr__ = __str__

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
        keys = self.modes.keys()
        keys.sort()
        return keys

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
        line = f.readline().strip()
        while line != "":
            index = line.find(":")
            mode  = line[0:index-1]
            comps = line[index+2:]
            self.add_mode(mode, eval(comps))
            line = f.readline().strip()
        f.close()
