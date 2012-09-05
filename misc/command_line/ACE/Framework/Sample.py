import os

class Sample(object):

    def __init__(self):
        self.atts = {}
        self.experiment = "input"

    def __str__(self):
        return '%s' % (self.atts)

    __repr__ = __str__

    def __getitem__(self, key):
        try:
            return self.atts[self.experiment][key]
        except KeyError:
            try:
                return self.atts['input'][key]
            except KeyError:
                return None

    def __setitem__(self, key, item):
        if not self.atts.has_key(self.experiment):
            self.atts[self.experiment] = {}
        self.atts[self.experiment][key] = item

    def __delitem__(self, key):
        if self.experiment != 'input':
            del self.atts[self.experiment][key]

    def get_experiment(self):
        return self.experiment

    def has_key(self, key):
        present = self.atts[self.experiment].has_key(key)
        if not present:
            present = self.atts['input'].has_key(key)
        return present

    def set_experiment(self, experiment):
        self.experiment = experiment

    def get(self, experiment, property):
        try:
            return self.atts[experiment][property]
        except:
            return None

    def set(self, experiment, property, value):
        if not self.atts.has_key(experiment):
            self.atts[experiment] = {}
        self.atts[experiment][property] = value

    def remove(self, experiment, key):
        if experiment != 'input':
            del self.atts[experiment][key]

    def remove_experiment(self, experiment):
        if experiment != 'input':
            del self.atts[experiment]

    def experiments(self):
        return self.atts.keys()

    def properties_for_experiment(self, experiment):
        try:
            return self.atts[experiment].keys()
        except:
            return None

    def properties(self):
        try:
            atts = []
            if self.experiment != "input":
                atts.extend(self.atts[self.experiment].keys())
            atts.extend(self.atts['input'].keys())
            return atts
        except:
            try:
                return self.atts['input'].keys()
            except:
                return None

    def save(self, path):
        sample_path = os.path.join(path, self.get("input", "id") + ".txt")
        f = open(sample_path, "w")
        f.write(repr(self.atts))
        f.flush()
        f.close()

    def load(self, file):
        f = open(file, "U")
        data = f.read()
        f.close()
        self.atts = eval(data)

if __name__ == '__main__':
    s = Sample()
    print "Invalid property reference returns None: " + str(s.get("input", "age"))
    s.set("input", "published age", 200000)
    s.set("input", "id", "1")
    s.set("36Cl-Default", "age", 200500)
    experiments = s.experiments()
    for experiment in experiments:
        print "Experiment: " + experiment
        properties = s.properties_for_experiment(experiment)
        print "    Properties:"
        for property in properties:
            print "        " + property
    for experiment in experiments:
        s.set_experiment(experiment)
        print "current experiment: " + experiment
        properties = s.properties()
        for property in properties:
            print "s['" + property + "'] = %s" % (s[property])
