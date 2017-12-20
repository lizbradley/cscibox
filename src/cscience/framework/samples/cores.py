from samples import Sample, VirtualSample

from cscience.framework import Collection, Run
from cscience.framework.datastructures import UncertainQuantity


class Core(Collection):
    _tablename = 'cores'

    @classmethod
    def connect(cls, backend):
        cls._table = backend.ctable(cls.tablename())

    #useful notes -- all keys (depths) are converted to millimeter units before
    #being used to reference a Sample value. Keys are still displayed to the
    #user in their selected unit, as those are actually pulled from the sample

    def __init__(self, name='New Core', plans=[], properties={}):
        self.name = name
        self.runs = set(plans)
        self.runs.add('input')
        self.properties = Sample()
        self.properties.update(properties)
        self.loaded = False
        super(Core, self).__init__([])

    def _dbkey(self, key):
        try:
            key = key.rescale('mm')
        except AttributeError:
            key = key
        return float(key)

    def _unitkey(self, depth):
        try:
            return float(depth.rescale('mm').magnitude)
        except AttributeError:
            return float(depth)

    @classmethod
    def makesample(cls, data):
        instance = Sample()
        instance.update(cls._table.loaddictformat(data))
        return instance

    def saveitem(self, key, value):
        return (self._dbkey(key), self._table.formatsavedict(value))

    def new_computation(self, cplan):
        """
        Add a new computation plan to this core, and return a VirtualCore
        with the requested plan set.
        """
        run = Run(cplan)
        self.runs.add(run.name)
        vc = VirtualCore(self, run.name)
        #convenience for this specific case -- the run is still in-creation,
        #so we need to keep the object around until it's done.
        vc.partial_run = run
        return vc

    @property
    def vruns(self):
        return [run for run in self.runs if run != 'input']

    def virtualize(self):
        """
        Returns a full set of virtual cores applicable to this Core
        This is currently returned as a list, sorted by run name.
        """
        if len(self.runs) == 1:
            #return input as its own critter iff it's the only plan in this core
            return [VirtualCore(self, 'input')]
        else:
            cores = []
            for run in sorted(self.runs):
                if run == 'input':
                    continue
                cores.append(VirtualCore(self, run))
            return cores

    def __getitem__(self, key):
        if key == 'all':
            print "Warning: use of 'all' key is deprecated. Use core.properties instead"
            return self.properties
        return self._data[self._unitkey(key)]

    def __setitem__(self, depth, sample):
        if depth == 'all':
            print "Warning: use of 'all' key is deprecated. Use core.properties instead"
            self.properties = sample
            return
        super(Core, self).__setitem__(self._unitkey(depth), sample)
        try:
            self.runs.update(sample.keys())
        except AttributeError:
            #not actually a run, just some background
            pass

    def add(self, sample):
        sample['input']['core'] = self.name
        self[sample['input']['depth']] = sample

    def forcesample(self, depth):
        try:
            return self[depth]
        except KeyError:
            s = Sample(exp_data={'depth': depth})
            self.add(s)
            return s

    def force_load(self):
        #not my favorite hack, but wevs.
        if not self.loaded:
            for sample in self:
                pass

    def __iter__(self):
        #if I'm getting all the keys, I'm going to want the values too, so
        #I might as well pull everything. Whee!
        if self.loaded:
            for key in self._data:
                yield key
        else:
            for key, value in self._table.iter_core_samples(self):
                if key == 'all':
                    #if we've got a core that used to have data in 'all', we want
                    #to put that data nicely in properties for great justice on
                    #load (should only happen on first load...)
                    sam = self.makesample(value)
                    #since it's not a "normal" sample anymore, it doesn't need
                    #depth and core, and life will be easier without them...
                    try:
                        del sam['input']['depth']
                        del sam['input']['core']
                    except KeyError:
                        pass
                    self.properties = sam
                    continue  #not actually part of our iteration, lulz
                numeric = UncertainQuantity(key, 'mm')
                self._data[self._unitkey(numeric)] = self.makesample(value)
                yield numeric
            self.loaded = True


class VirtualCore(object):
    #has a Core and an experiment, returns VirtualSamples for items instead
    #of Samples. Hurrah!
    def __init__(self, core, run):
        self.core = core
        self.run = run
        #make sure properties is at the right level!
        self.properties = VirtualSample(core.properties, run, core.properties)

    def __iter_ignored__(self):
        for key in self.core:
            if self[key].sample.ignored:
                yield self[key]

    def __iter__(self):
        for key in self.core:
            if not self[key].sample.ignored:
                yield self[key]

    def __getitem__(self, key):
        if key == 'run':
            return self.run
        return VirtualSample(self.core[key], self.run, self.core.properties)

    def keys(self):
        return self.core.keys()

    def createvalue(self, depth, key, value):
        sample = self.core.forcesample(depth)
        sample.setdefault(self.run, {})
        sample[self.run][key] = value
        return VirtualSample(sample, self.run, self.core.properties)


class Cores(Collection):
    _tablename = 'cores_map'

    @classmethod
    def connect(cls, backend):
        cls._table = backend.maptable(cls.tablename(), Core.tablename())

    @classmethod
    def loadkeys(cls, backend):
        try:
            data = cls._table.loadkeys()
        except NameError:
            cls.instance = cls.bootstrap(backend)
        else:
            instance = cls([])
            Core.connect(backend)
            for key, value in data.iteritems():
                instance[key] = Core(
                    key,
                    value.get('runs', []),
                    #TODO: does this need any formatting?
                    value.get('properties', {}))

            cls.instance = instance

    def delete_core(self, core):
        Core._table.delete_item(core.name)
        del self._data[core.name]

    def saveitem(self, key, value):
        runs = list(value.runs)
        properties = self._table.formatsavedict(value.properties)
        new_val = self._table.formatsavedict({
            'runs': runs,
            'properties': properties
        })
        return (key, new_val)

    def save(self, *args, **kwargs):
        super(Cores, self).save(*args, **kwargs)
        for core in self._data.itervalues():
            if core.loaded:
                kwargs['name'] = core.name
                core.save(*args, **kwargs)
