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
    """
    try:
        float(x)
        return '"%s"' % x
    except ValueError:
        return unicode(x)

_types = {'string':unicode, 'boolean':conv_bool, 'float':float, 'integer':int}
_formats = {'string':show_str, 'boolean':str,
            'float':lambda x: '%.2f' % x, 'integer':lambda x: '%d' % x}
#user-visible list of types
TYPES = ("String", "Integer", "Float", "Boolean")

#TODO: add units (?)
class Attribute(object):
    def __init__(self, name, type_='string', output=False):
        self.name = name
        self.type_ = type_.lower()
        self.output = output
        
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

class Attributes(Collection):
    #TODO: keep base/key attributes somewhere a little more obvious & use for eg
    #front for bisect
    _filename = 'atts'
    
    def __new__(self, *args, **kwargs):
        self.sorted_keys = ['id', 'depth', 'computation_plan']
        return super(Attributes, self).__new__(self, *args, **kwargs)
    def __init__(self, *args, **kwargs):
        self.sorted_keys = ['id', 'depth', 'computation_plan']
        super(Attributes, self).__init__(*args, **kwargs)
        
    
    def __iter__(self):
        for key in self.sorted_keys:
            yield self[key]
    def __setitem__(self, index, item):
        if index not in self.sorted_keys:
            #Keys (currently id, cplan, depth) stay out of sorting.
            bisect.insort(self.sorted_keys, index, 2)
        super(Attributes, self).__setitem__(index, item)

    def getkeyat(self, index):
        return self.sorted_keys[index]
    def indexof(self, key):
        return self.sorted_keys.index(key)

    def convert_value(self, att, value):
        """
        Takes a string and converts it to a Python-friendly value with
        type appropriate to the attribute (if known) or a string otherwise
        """
        return self[att].convert_value(value)
        
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
        instance = cls(id=Attribute('id', 'string', False),
                   depth=Attribute('depth', 'float', False),
                   computation_plan=Attribute('computation_plan', 'string', False))
        instance.sorted_keys = ['id', 'depth', 'computation_plan']


class Sample(dict):
    """
    A Sample is a set of data associated with a specific physical entity
    (for example, a single locus on a sediment core). Data associated with
    that Sample is organized by the source of data (system input or calculated
    via a particular CScience 'computation_plan').
    """

    def __init__(self, experiment='input', exp_data={}):
        self[experiment] = exp_data.copy()
        
    @property
    def name(self):
        return self['input']['id']
        
    def __delitem__(self, key):
        if key == 'input':
            raise KeyError()
        return super(Sample, self).__delitem__(key)

    def all_properties(self):
        props = set()
        for experiment, properties in self.iteritems():
            props.update(properties)
        return props
        

class VirtualSample(object):
    """
    A VirtualSample is a view of a sample with only one computation_plan. This allows
    viewing of sample data generated by multiple experiments (e.g. 'age') as
    distinct entities. Input data is available under all experiments.
    """
    #PERF: this is not a terribly efficient class/abstraction; if it turns out
    #to be a memory or performance bottleneck various elements can be made faster

    def __init__(self, sample, cplan):
        if len(sample) > 1 and cplan == 'input':
            raise ValueError()#?
        self.sample = sample
        self.computation_plan = cplan
        
    def remove_exp_intermediates(self):
        for key in self.sample[self.computation_plan].keys():
            if not cscience.datastore.sample_attributes[key].output:
                del self[key]
        
    def __getitem__(self, key):
        if key == 'computation_plan':
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

class Samples(Collection):
    _filename = 'samples'
        
class Group(set):
    def __init__(self, name):
        self.name = name

class Groups(Collection):
    _filename = 'groups'
