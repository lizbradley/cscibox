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
import cscience.datastore
import quantities as pq
import numpy as np
from cscience.framework import Collection



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

#Add units woo
micrograms = pq.UnitMass('micrograms', pq.gram*pq.micro, symbol='ug')
kiloyears = pq.UnitTime('kiloyears', pq.year*pq.kilo, symbol='ky')
megayears = pq.UnitTime('megayears', pq.year*pq.mega, symbol='My')

len_units = ('millimeters', 'centimeters', 'meters')
time_units = ('years', 'kiloyears', 'megayears')
mass_units = ('micrograms', 'milligrams', 'grams', 'kilograms')
loc_units = ('degrees',)
standard_cal_units = ('dimensionless',) + len_units + time_units + mass_units + loc_units
unitgroups = (len_units, time_units, mass_units)

def get_conv_units(unit):
    """
    Returns a list of units that can be converted to/from the passed unit
    """
    unit = str(unit)
    for group in unitgroups:
        if unit in group:
            return group
    return (unit,)

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


base_atts = ['depth', 'computation plan']
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
            #Keys (currently cplan, depth) stay out of sorting.
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
    via a particular CScience 'computation plan').
    """

    def __init__(self, experiment='input', exp_data={}):
        self[experiment] = exp_data.copy()

    @property
    def name(self):
        return '%s:%d' % (self['input']['core'], self['input']['depth'])

    def __delitem__(self, key):
        raise NotImplementedError('sample data deletion is a no-no!')


#TODO: these /really/ need to live elsewhere!
class UncertainQuantity(pq.Quantity):

    def __new__(cls, data, units='', uncertainty=0, dtype='d', copy=True):
        ret = pq.Quantity.__new__(cls, data, units, dtype, copy)
        ret.uncertainty = Uncertainty(uncertainty, units)
        return ret

    def __add__(self, other):
        # If there is no uncertainty on other
        if (not hasattr(other, "uncertainty")) or (not other.uncertainty.magnitude):
            mag = super(UncertainQuantity, self).__add__(other)
            return UncertainQuantity(mag, units=mag.units, uncertainty = self.uncertainty)

        #okay, so this should handle the units okay...
        mag = super(UncertainQuantity, self).__add__(other)
        if len(self.uncertainty.magnitude) == 1 and \
           len(other.uncertainty.magnitude) == 1:
              #now, new uncertainty is the two squared, added, sqrted
            error = float(np.sqrt(self.uncertainty.magnitude[0] ** 2 +
                                  other.uncertainty.magnitude[0] ** 2))
        else:
            stup = self.uncertainty.get_mag_tuple()
            otup = other.uncertainty.get_mag_tuple()
            error = [float(np.sqrt(stup[0] ** 2 + otup[0] ** 2)),
                     float(np.sqrt(stup[1] ** 2 + otup[1] ** 2))]
        return UncertainQuantity(mag, units=mag.units, uncertainty=error)

    def __neg__(to_negate):
        return UncertainQuantity(super(UncertainQuantity, to_negate).__neg__(),
                                 units=to_negate.units,
                                 uncertainty=to_negate.uncertainty.magnitude)

    def unitless_normal(self):
        """
        Get the value and a one-dimensional error of this quantity, without
        units. This is useful when you know the value you have should have a
        Gaussian error distribution and you need the values stripped of metadata
        for computation ease
        """
        value = self.magnitude
        uncert = np.average(self.uncertainty.get_mag_tuple())
        return (value, uncert)

    def __repr__(self):
        return '%s(%s, %s, %s)'%(
            self.__class__.__name__,
            repr(self.magnitude),
            self.dimensionality.string,
            repr(self.uncertainty)
        )

    #Copy pasted from the superclass to get the overwriting of (the setter of) units to work.
    @property
    def units(self):
        return pq.Quantity(1.0, (self.dimensionality))
    @units.setter
    #End the copy paste above!
    def units(self, new_unit):
        #Copy pasted from the superclass function we're overwriting
        try:
            assert not isinstance(self.base, pq.Quantity)
        except AssertionError:
            raise ValueError('can not modify units of a view of a Quantity')
        try:
            assert self.flags.writeable
        except AssertionError:
            raise ValueError('array is not writeable')
        to_dims = pq.quantity.validate_dimensionality(new_unit)
        if self._dimensionality == to_dims:
            return
        to_u = pq.Quantity(1.0, to_dims)
        from_u = pq.Quantity(1.0, self._dimensionality)
        try:
            cf = pq.quantity.get_conversion_factor(from_u, to_u)
        except AssertionError:
            raise ValueError(
                'Unable to convert between units of "%s" and "%s"'
                %(from_u._dimensionality, to_u._dimensionality)
            )
        mag = self.magnitude
        mag *= cf
        self._dimensionality = to_u.dimensionality
        #END copy paste
        self.uncertainty.units(new_unit) #All of that so we could run this line when our units were changed.

    def __getstate__(self):
        """
        Return the internal state of the quantity, for pickling
        purposes.

        """
        cf = 'CF'[self.flags.fnc]
        state = (1,
                 self.shape,
                 self.dtype,
                 self.flags.fnc,
                 self.tostring(cf),
                 self._dimensionality,
                 self.uncertainty
                 )
        return state

    def __setstate__(self, state):
        (ver, shp, typ, isf, raw, units, uncert) = state
        np.ndarray.__setstate__(self, (shp, typ, isf, raw))
        self.uncertainty = uncert
        self._dimensionality = units

    def unitless_str(self):
        my_str = ('%.2f'%self.magnitude.item()).rstrip('0').rstrip('.')
        if hasattr(self, 'uncertainty'):
            return '%s%s'%(my_str, str(self.uncertainty))
        else:
            return '%s%s'%(my_str, "0")

    def __str__(self):
        dims = self.dimensionality.string
        if dims == 'dimensionless':
            return self.unitless_str()
        return '%s %s'%(self.unitless_str(), dims)

class Uncertainty(object):

    def __init__(self, uncert, units):
        self.distribution = None
        self.magnitude = []
        self._units = units
        if uncert:
            try:
                mag = uncert.error
            except AttributeError:
                #TODO: this crashes when I try to pass a Quantity as uncert,
                #because apparently __len__ is defined but it is an unsized
                #object??? anyway, that ought to be a sane param here, so I
                #should fix that.
                if not hasattr(uncert,'__len__'):
                    mag = [uncert]
                else:
                    if len(uncert)>2:
                        raise ValueError('Uncert must be a single value, '
                             'pair of values, or matplotlib distribution')
                    else:
                        mag = uncert
            else:
                self.distribution = uncert
            self.magnitude = [pq.Quantity(val, units) for val in mag]

    def __add__(self,other):
        # TODO make add much more robust
        mag = self.magnitude[0] + other.magnitude[0]
        return(Uncertainty(mag, self._units))

    def units(self, new_unit):
        for quant in self.magnitude:
            quant.units = new_unit
        self._units = new_unit

    def __float__(self):
        return self.magnitude[0].magnitude.item()

    def __repr__(self):
        if self.distribution:
            uncert = repr(self.distribution)
        else:
            uncert = str(self.magnitude)
        return '%s(%s)' % (self.__class__.__name__, uncert)

    def get_mag_tuple(self):
        #strip units for great justice (AKA graphing sanity)
        if not self.magnitude:
            return (0, 0)
        elif len(self.magnitude)>1:
            return (self.magnitude[0].magnitude, self.magnitude[1].magnitude)
        else:
            return (self.magnitude[0].magnitude, self.magnitude[0].magnitude)

    def as_single_mag(self):
        if not self.magnitude:
            return 0
        else:
            return float(sum([it.magnitude for it in self.magnitude])) / len(self.magnitude)

    def __str__(self):
        if not self.magnitude:
            return ''
        elif len(self.magnitude) == 1:
            if not self.magnitude[0]:
                return ''
            else:
                mag = self.magnitude[0].magnitude.item()
                return '+/-' + ('%.2f'%mag).rstrip('0').rstrip('.')
        else:
            return '+{}/-{}'.format(*[('%.2f'%mag.magnitude). \
                            rstrip('0').rstrip('.') for mag in self.magnitude])

class VirtualSample(object):
    """
    A VirtualSample is a view of a sample with only one computation plan. This allows
    viewing of sample data generated by multiple cplans (e.g. 'age') as
    distinct entities. Input data is available under all cplans.
    """
    #PERF: this is not a terribly efficient class/abstraction; if it turns out
    #to be a memory or performance bottleneck various elements can be made faster

    def __init__(self, sample, cplan, core_wide={}):
        if len(sample) > 1 and cplan == 'input':
            raise ValueError()#?
        self.sample = sample
        self.computation_plan = cplan
        self.core_wide = core_wide
        #Make sure the cplan specified is a working entry in the sample
        self.sample.setdefault(self.computation_plan, {})
        self.dst = cscience.datastore.Datastore()

    def __getitem__(self, key):
        if key == 'computation plan':
            return self.computation_plan
        try:
            att = self.dst.sample_attributes[key]
        except KeyError:
            pass
        else:
            if att.is_virtual:
                return att.compose_value(self)
        try:
            return self.sample[self.computation_plan][key]
        except KeyError:
            try:
                return self.sample['input'][key]
            except KeyError:
                try:
                    return self.core_wide[self.computation_plan][key]
                except KeyError:
                    try:
                        return self.core_wide['input'][key]
                    except KeyError:
                        return None
    def __setitem__(self, key, item):
        self.sample[self.computation_plan][key] = item
    def __delitem__(self, key):
        del self.sample[self.computation_plan][key]

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
        keys = set(self.sample[self.computation_plan].keys())
        keys.update(self.sample['input'].keys())
        return keys

    def keys(self):
        keys = self.sample_keys()
        #now add the things that are core-wide....
        keys.update(self.core_wide[self.computation_plan].keys())
        keys.update(self.core_wide['input'].keys())
        return keys

    def search(self, value, view=None, exact=False):
        if not view:
            view = cscience.datastore.Datastore().views['All']
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
        self.cplans = set(plans)
        self.cplans.add('input')
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
        self.cplans.add(cplan)
        return VirtualCore(self, cplan)

    def virtualize(self):
        """
        Returns a full set of virtual cores applicable to this Core
        This is currently returned as a list, sorted by computation plan name.
        """
        if len(self.cplans) == 1:
            #return input as its own critter iff it's the only plan in this core
            return [VirtualCore(self, 'input')]
        else:
            cores = []
            for plan in sorted(self.cplans):
                if plan == 'input':
                    continue
                cores.append(VirtualCore(self, plan))
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
            self.cplans.update(sample.keys())
        except AttributeError:
            #not actually a computation plan, just some background
            pass

    def add(self, sample):
        sample['input']['core'] = self.name
        self[sample['input']['depth']] = sample

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
    def __init__(self, core, cplan):
        self.core = core
        self.computation_plan = cplan

    def __iter__(self):
        for key in self.core:
            yield self[key]
    def __getitem__(self, key):
        if key == 'computation plan':
            return self.computation_plan
        return VirtualSample(self.core[key], self.computation_plan, self.core['all'])


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
                instance[key] = Core(key, set(value.get('cplans', [])))

            cls.instance = instance

    def saveitem(self, key, value):
        return (key, self._table.formatsavedict({'cplans':list(value.cplans)}))
    def save(self, *args, **kwargs):
        super(Cores, self).save(*args, **kwargs)
        for core in self._data.itervalues():
            if core.loaded:
                kwargs['name'] = core.name
                core.save(*args, **kwargs)
