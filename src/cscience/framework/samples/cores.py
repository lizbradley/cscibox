from samples import Sample, VirtualSample

import coremetadata as mData

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

    def __init__(self, name='New Core', plans=[]):
        self.name = name
        self.runs = set(plans)
        self.mdata = mData.Core(name)
        self.runs.add('input')
        self.loaded = False
        super(Core, self).__init__([])
        self.add(Sample(exp_data={'depth':'all'}))

    def _dbkey(self, key):
        if key == 'all':
            return key
        try:
            key = key.rescale('mm')
        except AttributeError:
            key = key
        return float(key)

    def _unitkey(self, depth):
        if depth == 'all':
            return depth
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
        try:
            return self._data[self._unitkey(key)]
        except KeyError:
            #all cores should have an 'all' depth; this adds it for legacy cores
            if self.loaded and key == 'all':
                self.add(Sample(exp_data={'depth':'all'}))
                return self._data['all']
            else:
                raise
    def __setitem__(self, depth, sample):
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
            s = Sample(exp_data={'depth':depth})
            self.add(s)
            return s

    def __iter__(self):
        #if I'm getting all the keys, I'm going to want the values too, so
        #I might as well pull everything. Whee!
        if self.loaded:
            for key in self._data:
                if key != 'all':
                    yield key
        else:
            for key, value in self._table.iter_core_samples(self):
                if key != 'all':
                    numeric = UncertainQuantity(key, 'mm')
                    self._data[self._unitkey(numeric)] = self.makesample(value)
                    yield numeric
                else:
                    self._data['all'] = self.makesample(value)
            self.loaded = True

class VirtualCore(object):
    #has a Core and an experiment, returns VirtualSamples for items instead
    #of Samples. Hurrah!
    def __init__(self, core, run):
        self.core = core
        self.run = run

    def __iter__(self):
        for key in self.core:
            yield self[key]
    def __getitem__(self, key):
        if key == 'run':
            return self.run
        return VirtualSample(self.core[key], self.run, self.core['all'])

    def keys(self):
        keys = self.core.keys()
        try:
            keys.remove('all')
        except ValueError:
            pass
        return keys

    def createvalue(self, depth, key, value):
        sample = self.core.forcesample(depth)
        sample.setdefault(self.run, {})
        sample[self.run][key] = value
        return VirtualSample(sample, self.run, self.core['all'])

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
                instance[key] = Core(key, value.get('runs', []))

            cls.instance = instance

    def delete_core(self, core):
        Core._table.delete_item(core.name)
        del self._data[core.name]

    def saveitem(self, key, value):
        return (key, self._table.formatsavedict({'runs':list(value.runs)}))
    def save(self, *args, **kwargs):
        super(Cores, self).save(*args, **kwargs)
        for core in self._data.itervalues():
            if core.loaded:
                kwargs['name'] = core.name
                core.save(*args, **kwargs)
