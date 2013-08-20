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
# import decimal

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

standard_cal_units = ('dimensionless','millimeters', 'centimeters', 'meters', 'days', 'years', 
                      'kiloyears', 'megayears', 'grams', 'kilograms', 'mole', 
                      )
#If the units above aren't understood by quantities by default, add them below.
kiloyears = pq.UnitTime('kiloyears', pq.year*1000, symbol='ky')
megayears = pq.UnitTime('megayears', pq.year*1000000, symbol='My')

class Attribute(object):
    
    #???
    #If I construct this without explicitly passing [] as the fifth argument 
    #(ie., if I rely on the default), all Attributes are using the same list 
    #as their children.
    #I fixed it by changing children's default to None and making it an empty
    #list if children is None, but would like to understand why.
    #???
    def __init__(self, name, type_='string', unit='', output=False, 
                 children=None, parent=None):
        if children is None:
            children = []
        self.name = name
        self.type_ = type_.lower()
        self.unit = unit
        self.output = output
        self.children = children
        self.parent = parent
        
    def get_children(self):
        return self.children
    
    def set_parent(self, parent):
        self.parent = parent
        
    def get_parent(self):
        return self.parent
    
    def add_child(self, att):
        self.children.append(att)
        att.set_parent(self)
    
    def remove_child(self, att):
        self.children.remove(att)
        att.set_parent(None)
            
    def remove_all_children(self):
        for child in self.children:
            child.set_parent(None)
        self.children = []
        
    @property
    def in_use(self):
        """
        Determine if an attribute is in use. An attribute is considered to
        be in use if:
        - it is marked as an output attribute
        - it is used by a view (that is not the 'All' view)
        - it is used by any sample
        
        Type of usage or blank string is returned
        """
        #TODO: this is not exactly efficient code...
        if self.output:
            return "Output Attribute" 
        for view in cscience.datastore.views.itervalues():
            if view.name == "All":
                continue
            if self.name in view:
                return "Used by View '%s'" % (view.name)
        for core in cscience.datastore.cores.itervalues():
            for sample in core:
                if self.name in sample.all_properties():
                    #changed the below from ...sample['input']['id'] because
                    #the 'id' key wasn't getting a value anywhere I could find.
                    return "Used by Sample '%s'" % (sample['input']['depth'])       
        return ''
    
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

base_atts = ['depth', 'computation plan']
class Attributes(Collection):
    _filename = 'atts'
    
    def __new__(self, *args, **kwargs):
        self.sorted_keys = base_atts[:]
        self.base_atts = base_atts
        return super(Attributes, self).__new__(self, *args, **kwargs)

    def __iter__(self):
        for key in self.sorted_keys:
            yield self[key]
    def __setitem__(self, index, item):
        if index not in self.sorted_keys:
            #Keys (currently cplan, depth) stay out of sorting.
            bisect.insort(self.sorted_keys, index, len(base_atts))
        return super(Attributes, self).__setitem__(index, item)
    def __delitem__(self, key):
        if key in base_atts:
            raise ValueError('Cannot remove attribute %s' % key)
        if self[key].get_parent():
            self[key].get_parent().remove_child(self[key])
        children = self[key].get_children()
        for child in children[:]:
            del self[child.name]
        self.sorted_keys.remove(key)
        return super(Attributes, self).__delitem__(key)
    
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
        
    def format_value(self, att, value):
        """
        Formats a Python attribute value for user visibility. Specifically:
        None -> 'N/A'
        numbers are nicely formatted
        strings that look like numbers are surrounded by quotes
        """
        return self[att].format_value(value)

    @classmethod
    def default_instance(cls):
        instance = cls()
        instance.sorted_keys = base_atts[:]
        instance['depth'] = Attribute('depth', 'float', 'centimeters', False)
        instance['computation plan'] = Attribute('computation plan', 'string', 
                                                                '', False)
        return instance


class Sample(dict):
    """
    A Sample is a set of data associated with a specific physical entity
    (for example, a single locus on a sediment core). Data associated with
    that Sample is organized by the source of data (system input or calculated
    via a particular CScience 'computation plan').
    """

    def __init__(self, experiment='input', exp_data={}):
        used_keys = set()
        self[experiment] = exp_data.copy()
        
    @property
    def name(self):
        return '%s:%d' % (self['input']['core'], self['input']['depth'])
        
    def __delitem__(self, key):
        if key == 'input':
            raise KeyError()
        return super(Sample, self).__delitem__(key)

    def all_properties(self):
        props = set()
        for experiment, properties in self.iteritems():
            props.update(properties)
        return props
        

class UncertainQuantity(pq.Quantity):
    
    def __new__(cls, data, units='', uncertainty=0, dtype='d', copy=True):
        ret = pq.Quantity.__new__(cls, data, units, dtype, copy)
        ret.uncertainty = Uncertainty(uncertainty, units)
        return ret
    
    def __repr__(self):
        return '%s(%s, %s, %s)'%(
            self.__class__.__name__,
            repr(self.magnitude),
            self.dimensionality.string,
            repr(self.uncertainty)
        )
        
    @property
    def units(self):
        return pq.Quantity(1.0, (self.dimensionality))
    @units.setter
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
        self.uncertainty.units(new_unit)
        
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
        
    def __str__(self):
        dims = self.dimensionality.string
        #Sorry about the magnitude.magnitude thing. uncertainty.magnitude is a
        #pq.Quantity object so that our uncertainty has units. In that object, 
        #they use .magnitude to refer to the uncertainty's dimensionless magnitude.
        return '%s%s %s'%(str(self.magnitude), 
                             str(self.uncertainty), 
                             dims)

class Uncertainty(object):
    
    def __init__(self, uncert, units):
        mag = 0
        self.distribution = None
        try:
            mag = uncert.std()
        except AttributeError:
            if not hasattr(uncert,'__len__'):
                mag = [uncert]
            else:
                if len(uncert)>2:
                    raise ValueError('Uncert must be a single value, pair of values, or matplotlib distribution')
                else:
                    mag = uncert
        else:
            self.distribution = uncert
        self.magnitude = [pq.Quantity(val, units) for val in mag]
        # Trying to be pythonic about allowing uncert to be a single value or a 
        # distribution. If this was java I'd overload the constructor.
        
    def units(self, new_unit):
        for quant in self.magnitude:
            quant.units = new_unit
        
    def __repr__(self):
        if self.distribution is not None:
            uncert = repr(self.distribution)
        else:
            uncert = str(self.magnitude)
        return '%s(%s)' % (self.__class__.__name__, uncert)
        
    def get_mag_tuple(self):
        if len(self.magnitude)>1:
            return (self.magnitude[0], self.magnitude[1])
        else:
            return (self.magnitude[0], self.magnitude[0])
    
        
    def __str__(self):
        if len(self.magnitude) is 1:
            if self.magnitude[0] is 0:
                return ''
            else:
                return '+/-' + ('%f'%self.magnitude[0].magnitude).rstrip('0').rstrip('.')
        else:
            #Sorry about the magnitude.magnitude thing. uncertainty.magnitude is a
            #pq.Quantity object so that our uncertainty has units. In that object, 
            #they use .magnitude to refer to the uncertainty's dimensionless magnitude.
            #Also, that rstrip stuff will probably turn 2500 in to 25, but I think 
            #since I format it as a float first I'm okay.
            return '+{}/-{}'.format(*[('%f'%mag.magnitude). \
                            rstrip('0').rstrip('.') for mag in self.magnitude])
            

class JohnQuantity(float):
    
    def __new__(cls, value, error):
        try: 
            return float.__new__(cls, value)
        except (TypeError, ValueError): 
            raise My_Error(value)
            
    def __init__(self, value, error):
        try:
            error_length = len(error)
        except (TypeError):
            error_length = 1
            
        #TODO: handle error as a function.
        if error_length is 1:
            self.lower_bound = error
            self.upper_bound = error
        elif error_length is 2:
            self.lower_bound = error[0]
            self.upper_bound = error[1]
        else: print("Unexpected error length: ",error_length)
        
    def get_error(self):
        return (self.lower_bound, self.upper_bound)
    
    def __str__(self):
        if self.lower_bound is self.upper_bound:
            if self.lower_bound is 0:
                error_string = ''
            else:
                error_string = '+/-' + str(self.lower_bound)
        else:
            error_string = '+' + str(self.upper_bound) + ' / -' + str(self.lower_bound)
        return super.__str__(self) + error_string
        
class VirtualSample(object):
    """
    A VirtualSample is a view of a sample with only one computation plan. This allows
    viewing of sample data generated by multiple cplans (e.g. 'age') as
    distinct entities. Input data is available under all cplans.
    """
    #PERF: this is not a terribly efficient class/abstraction; if it turns out
    #to be a memory or performance bottleneck various elements can be made faster

    def __init__(self, sample, cplan):
        if len(sample) > 1 and cplan == 'input':
            raise ValueError()#?
        self.sample = sample
        self.computation_plan = cplan
        #Make sure the cplan specified is a working entry in the sample
        self.sample.setdefault(self.computation_plan, {})
        
    def remove_exp_intermediates(self):
        for key in self.sample[self.computation_plan].keys():
            if not cscience.datastore.sample_attributes[key].output:
                del self[key]
        
    def __getitem__(self, key):
        if key == 'computation plan':
            return self.computation_plan
        try:
            return self.sample[self.computation_plan][key]
        except KeyError:
            try:
                return self.sample['input'][key]
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

    def keys(self):
        keys = set(self.sample[self.computation_plan].keys())
        keys.update(self.sample['input'].keys())
        return keys
    
    def search(self, value, view=None, exact=False):
        if not view:
            view = cscience.datastore.views['All']
        for att in view:
            val = str(self[att] or '')
            if val == value or (not exact and value in val):
                return att
        return None
        
class Core(dict):
    
    def __new__(cls, *args, **kwargs):
        self = super(Core, cls).__new__(cls, *args, **kwargs)
        self.cplans = set(['input'])
        return self
    
    def __init__(self, name='New Core'):
        self.name = name
        self.cplans = set(['input'])
        
    def new_computation(self, cplan):
        """
        Add a new computation plan to this core, and return a VirtualCore
        with the requested plan set.
        Raises a ValueError if the requested plan is already represented in
        this Core.
        """
        if cplan in self.cplans:
            raise ValueError('Cannot overwrite existing computations')
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
        
    def strip_experiment(self, exp):
        print('In Core.strip_experiment, exp: %s.'%exp)
        if exp == 'input':
            raise KeyError()
        if exp not in self.cplans:
            raise KeyError()
                    
        for sample in self:
            try:
                del sample[exp]
            except KeyError:
                pass
        self.cplans.remove(exp)
        
    def __setitem__(self, depth, sample):
        super(Core, self).__setitem__(depth, sample)
        self.cplans.update(sample.keys())
                
    def add(self, sample):
        sample['input']['core'] = self.name
        self[sample['input']['depth']] = sample
        
    def __iter__(self):
        for key in sorted(self.keys()):
            yield self[key]
            
class VirtualCore(object):
    #has a Core and an experiment, returns VirtualSamples for items instead
    #of Samples. Hurrah!
    def __init__(self, core, cplan):
        self.core = core
        self.computation_plan = cplan
        
    def keys(self):
        return self.core.keys()
    def __iter__(self):
        for key in sorted(self.keys()):
            yield self[key]
    def __getitem__(self, key):
        if key == 'computation plan':
            return self.computation_plan
        return VirtualSample(self.core[key], self.computation_plan)
    def strip_experiment(self, exp):
        return self.core.strip_experiment(exp)
        

class Cores(Collection):
    #TODO: unlike all the other Collections, it probably does make sense for
    #cores to be stored as cores/corename.csc...
    _filename = 'cores'
