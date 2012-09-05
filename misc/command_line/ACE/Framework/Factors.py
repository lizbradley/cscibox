import os
import os.path

from ACE.Framework import Factor

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
        factors_path =  os.path.join(path, "factors")

        if not os.path.exists(factors_path):
            os.mkdir(factors_path)

        keys = self.names()

        # delete factors no longer in self.factors()
        items = os.listdir(factors_path)
        to_delete = [file for file in items if not file[0:len(file)-4] in keys]
        for file in to_delete:
            os.remove(os.path.join(factors_path, file))

        for name in keys:
            factor = self.get(name)
            factor.save(factors_path)

    def load(self, path):
        factors_path =  os.path.join(path, "factors")

        if not os.path.exists(factors_path):
            os.mkdir(factors_path)

        items   = os.listdir(factors_path)
        factors = [item for item in items if item.endswith('.txt')]
        for name in factors:
            factor = Factor(name[0:len(name)-4])
            factor.load(os.path.join(factors_path, name))
            self.add(factor)

if __name__ == '__main__':
    f = Factors()
    f.load('.')
    names = f.names()
    for name in names:
        factor = f.get(name)
        print "%s:" % (factor.get_name())
        modes = factor.get_mode_names()
        for mode in modes:
            print "\t%s" % (mode)
            comps = factor.get_components_for_mode(mode)
            for comp in comps:
                print "\t\t%s" % (comp)
    f.save('.')
