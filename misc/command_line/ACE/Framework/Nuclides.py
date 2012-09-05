import os
import os.path

from ACE.Framework import Nuclide

class Nuclides(object):

    def __init__(self):
        self.nuclides = {}
        default_nuclide = Nuclide('ALL')
        self.add(default_nuclide)

    def add(self, nuclide):
        self.nuclides[nuclide.name()] = nuclide

    def contains(self, name):
        return name in self.nuclides
        
    def get(self, name):
        return self.nuclides[name]
        
    def remove(self, name):
        del self.nuclides[name]

    def names(self):
        names = self.nuclides.keys()
        names.sort()
        return names
        
    def save(self, path):
        nuclides_path = os.path.join(path, 'nuclides.txt')
        nuclides_file = open(nuclides_path, "w")

        for name in self.names():
            nuclide      = self.get(name)
            nuclides_file.write('BEGIN NUCLIDE')
            nuclides_file.write(os.linesep)
            nuclide.save(nuclides_file)
            nuclides_file.write('END NUCLIDE')
            nuclides_file.write(os.linesep)
        
        nuclides_file.flush()
        nuclides_file.close()

    def load(self, path):
        nuclides_path = os.path.join(path, 'nuclides.txt')
        nuclides_file = open(nuclides_path, "U")

        line = nuclides_file.readline().strip()
        while line != "":
            while line != "END NUCLIDE":
                nuclide = Nuclide()
                nuclide.load(nuclides_file)
                self.add(nuclide)
                line = nuclides_file.readline().strip()
            line = nuclides_file.readline().strip()
        nuclides_file.close()
