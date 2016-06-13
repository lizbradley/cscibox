#TODO: split this out appropriately
"""
samples.py

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

import bisect
import time
import cscience.datastore
import numpy as np

import coremetadata as mData

from cscience.framework import Collection, Run
from cscience.framework.datastructures import UncertainQuantity

def conv_bool(x):
    if not x:
        return None
    elif x[0].lower() in 'pyst1':
        return True
    else:
        return False
def show_str(x):
    """
    Put numbers handled as strings in quotes to make visibility much saner
    Edit -- this is actually pretty awful, in practice, so let's just use plain
    strings.
    """
    return unicode(x)

_types = {'string':unicode, 'boolean':conv_bool, 'float':float, 'integer':int}
_comps = {'string':unicode}
_formats = {'string':show_str, 'boolean':str,
            'float':lambda x: '%.2f' % x, 'integer':lambda x: '%d' % x}
#user-visible list of types
TYPES = ("String", "Integer", "Float", "Boolean")
#TODO: add a type for object...

class Attribute(object):

    def __init__(self, name, type_='string', unit='', output=False, has_error=False):
        self.name = name
        self.type_ = type_.lower()
        self.unit = unit
        self.output = output
        self.has_error = has_error

    def is_numeric(self):
        return self.type_ in ('float', 'integer')

    @property
    def in_use(self):
        """
        Determine if an attribute is in use.
        Type of usage or blank string is returned
        """
        return 'All attributes now considered in use for sanity'

    @property
    def is_virtual(self):
        return False

    @property
    def compare_type(self):
        """
        Gives the type used for this attribute to compare it to other
        attributes/values.
        """
        try:
            return _comps[self.type_]
        except KeyError:
            return float

    def convert_value(self, value):
        """
        Takes a string and converts it to a Python-friendly value with
        type appropriate to the attribute (if known) or a string otherwise
        """
        try:
            return _types[self.type_](value)
        except KeyError:
            #means attribute not present, but honestly, SO?
            return unicode(value)
        #ValueError also possible; that should be re-raised

    def format_value(self, value):
        """
        Formats a Python attribute value for user visibility. Specifically:
        None -> 'N/A'
        numbers are nicely formatted
        strings that look like numbers are surrounded by quotes
        """
        if value is None:
            return 'N/A'
        try:
            return _formats[self.type_](value)
        except KeyError:
            return show_str(value)

class VirtualAttribute(object):
    """
    A Virtual Attribute is a conceptual object that shows (hierarchically) one
    of some set of attributes from a sample. Conceptually, when a sample is
    asked for its value for an Attribute that is virtual, the value returned
    will be the value of the first non-null attribute in said sample from the
    list of combined attributes within the virtual attribute.

    (this is set up to work only on virtual samples, but since that's what
    you'll have in basically any case here anyway, that's not to be worried
    about)
    """
    def __init__(self, name, type_='string', aggatts=[]):
        self.name = name
        self.type_ = type_.lower()
        self.aggatts = aggatts
        #TODO: make this be smrt.
        self.unit = ''

    def is_numeric(self):
        dst = cscience.datastore.Datastore()
        return all([dst.sample_attributes[att].is_numeric() for att in self.aggatts])

    @property
    def is_virtual(self):
        return True

    def compose_value(self, sample):
        for att in self.aggatts:
            if sample[att] is not None:
                return sample[att]
        return None


base_atts = ['depth', 'run']
def basesorter(a, b):
    if a not in base_atts and b not in base_atts:
        return cmp(a, b)
    if a in base_atts:
        if b in base_atts:
            return cmp(base_atts.index(a), base_atts.index(b))
        return -1
    return 1
class Attributes(Collection):
    _tablename = 'atts'

    def __new__(self, *args, **kwargs):
        instance = super(Attributes, self).__new__(self, *args, **kwargs)
        instance.sorted_keys = base_atts[:]
        instance.base_atts = base_atts
        return instance
    def __init__(self, *args, **kwargs):
        super(Attributes, self).__init__(*args, **kwargs)
        self.sorted_keys = sorted(self.keys(), cmp=basesorter)

    def __iter__(self):
        for key in self.sorted_keys:
            yield self[key]
    def __setitem__(self, index, item):
        if index not in self.sorted_keys:
            #Keys (currently run, depth) stay out of sorting.
            bisect.insort(self.sorted_keys, index, len(base_atts))
        return super(Attributes, self).__setitem__(index, item)

    def byindex(self, index):
        return self[self.getkeyat(index)]
    def getkeyat(self, index):
        return self.sorted_keys[index]
    def indexof(self, key):
        return self.sorted_keys.index(key)

    def get_compare_type(self, att):
        return self[att].compare_type
    def convert_value(self, att, value):
        """
        Takes a string and converts it to a Python-friendly value with
        type appropriate to the attribute (if known) or a string otherwise
        """
        return self[att].convert_value(value)

    def get_unit(self, att):
        return self[att].unit
    def add_attribute(self, name, type, unit, isoutput, haserror):
        self[name] = Attribute(name, type, unit, isoutput, haserror)
    def add_virtual_att(self, name, aggregate):
        if aggregate:
            type_ = aggregate[0].type_
        else:
            type_ = 'string'
        #no unit
        self[name] = VirtualAttribute(name, type_, [agg.name for agg in aggregate])

    def virtual_atts(self):
        return sorted([att.name for att in self if att.is_virtual])

    def format_value(self, att, value):
        """
        Formats a Python attribute value for user visibility. Specifically:
        None -> 'N/A'
        numbers are nicely formatted
        strings that look like numbers are surrounded by quotes
        """
        return self[att].format_value(value)

    @classmethod
    def bootstrap(cls, connection):
        instance = super(Attributes, cls).bootstrap(connection)
        instance.sorted_keys = base_atts[:]
        instance['depth'] = Attribute('depth', 'float', 'centimeters')
        instance['run'] = Attribute('run')
        instance['computation plan'] = Attribute('computation plan')
        instance['Provenance'] = Attribute('Provenance')
        instance['Latitude'] = Attribute('Latitude', 'float', 'degrees')
        instance['Longitude'] = Attribute('Longitude', 'float', 'degrees')
        instance['Core GUID'] = Attribute('Core GUID')
        return instance


class Sample(dict):
    """
    A Sample is a set of data associated with a specific physical entity
    (for example, a single locus on a sediment core). Data associated with
    that Sample is organized by the source of data (system input or calculated
    via a particular CScience 'run').
    """

    def __init__(self, experiment='input', exp_data={}):
        self[experiment] = exp_data.copy()

    @property
    def name(self):
        return '%s:%d' % (self['input']['core'], self['input']['depth'])

    def __delitem__(self, key):
        raise NotImplementedError('sample data deletion is a no-no!')




class VirtualSample(object):
    """
    A VirtualSample is a view of a sample with only one run. This allows
    viewing of sample data generated by multiple runs (e.g. 'age') as
    distinct entities. Input data is available under all runs.
    """
    #PERF: this is not a terribly efficient class/abstraction; if it turns out
    #to be a memory or performance bottleneck various elements can be made faster

    def __init__(self, sample, run, core_wide={}):
        self.sample = sample
        self.run = run
        self.core_wide = core_wide
        #Make sure the run specified is a working entry in the sample
        self.sample.setdefault(self.run, {})
        self.dst = cscience.datastore.Datastore()

    def __getitem__(self, key):
        if key == 'run':
            #TODO: would it make life easier if this always returned the actual
            #run object? It might, but some testing is needed to make sure
            #that doesn't break various things....
            return self.run
        try:
            att = self.dst.sample_attributes[key]
        except KeyError:
            pass
        else:
            if att.is_virtual:
                return att.compose_value(self)
        try:
            return self.sample[self.run][key]
        except KeyError:
            try:
                return self.sample['input'][key]
            except KeyError:
                try:
                    return self.core_wide[self.run][key]
                except KeyError:
                    try:
                        return self.core_wide['input'][key]
                    except KeyError:
                        return None
    def __setitem__(self, key, item):
        self.sample[self.run][key] = item
    def __delitem__(self, key):
        del self.sample[self.run][key]

    def __contains__(self, key):
        return key in self.keys()
    def __len__(self):
        return len(self.keys())
    def __iter__(self):
        return iter(self.keys())

    def iteritems(self):
        for key in self.keys():
            yield (key, self[key])
    def itervalues(self):
        for key in self.keys():
            yield self[key]

    def sample_keys(self):
        keys = set(self.sample[self.run].keys())
        keys.update(self.sample['input'].keys())
        return keys

    def keys(self):
        keys = self.sample_keys()
        #now add the things that are core-wide....
        keys.update(self.core_wide[self.run].keys())
        keys.update(self.core_wide['input'].keys())
        return keys

    def setdefault(self, key, value):
        self.sample[self.run].setdefault(key, value)

    def search(self, value, view=None, exact=False):
        if not view:
            view = self.dst.views['All']
        for att in view:
            val = str(self[att] or '')
            if val == value or (not exact and value in val):
                return att
        return None

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
