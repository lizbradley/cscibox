"""
views.py

* Copyright (c) 2006-2015, University of Colorado.
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

import itertools
import cscience.datastore
from cscience.framework import Collection, DataObject

ops = (('==', '!=', '>', '>=', '<', '<=', 
        'Starts With', 'Ends With', 'Contains'),
       ('__eq__', '__ne__', '__gt__', '__ge__', '__lt__', '__le__', 
        'startswith', 'endswith', '__contains__'))

def operation_name(target):
    try:
        return ops[0][ops[1].index(target)]
    except ValueError:
        raise KeyError()
    
def named_operation(name):
    try:
        return ops[1][ops[0].index(name)]
    except ValueError:
        raise KeyError()

class FilterFilter(object):
    """
    Used for negating an existing Filter
    """

    def __init__(self, internal_filter='Select Filter', value=False, parent_name=None):
        self.filter = internal_filter
        try:
            self.show_value = value
        except ValueError:
            self.value = bool(value)
        self.parent_name = parent_name
        
    @property
    def item_choices(self):
        names = sorted(cscience.datastore.filters.keys())
        names.remove(self.parent_name)
        return ['Select Filter'] + names
    value_choices = ('False', 'True')
    comparators = ('==',)
    @property
    def show_item(self):
        return self.filter
    @show_item.setter
    def show_item(self, value):
        self.filter = value
    @property
    def show_value(self):
        return str(self.value)
    @show_value.setter
    def show_value(self, value):
        self.value = bool(self.value_choices.index(value))
    @property
    def show_op(self):
        return self.comparators[0]
        
    
    def apply(self, s):
        return self.filter.apply(s) == self.value
    def copy(self):
        return FilterFilter(self.filter, self.value)
    @property
    def description(self):
        return self.value and self.filter.description() or \
                "NOT (%s)" % self.filter.description()
    def depends_on(self, filter_name):
        return self.filter.name == filter_name
    
class FilterItem(object):

    def __init__(self, key='computation plan', op='__eq__', value='<EDIT ME>'):
        self.key = key
        try:
            self.show_op = op
        except KeyError:
            self.op_name = op
            self.operation = getattr(unicode, op)
        self.show_value = value
        
    def __getstate__(self):
        state = self.__dict__
        #trying to save the comparator function here makes for sads, so...
        del state['operation']
        state['ctype'] = self.ctype
        return state
    
    def __setstate__(self, state):
        self.key = state['key']
        self.op_name = state['op_name']
        self.operation = getattr(state['ctype'], self.op_name)
        self.value = state['value']
            
    @property
    def item_choices(self):
        return cscience.datastore.sample_attributes.sorted_keys
    value_choices = None
    comparators = ops[0]
    @property
    def show_item(self):
        return self.key
    @show_item.setter
    def show_item(self, value):
        self.key = value
    @property
    def show_value(self):
        return cscience.datastore.sample_attributes.format_value(self.key, self.value)
    @show_value.setter
    def show_value(self, value):
        self.value = cscience.datastore.sample_attributes.convert_value(self.key, value)
    @property
    def show_op(self):
        return operation_name(self.op_name)
    @show_op.setter
    def show_op(self, value):
        self.op_name = named_operation(value)
        self.operation = getattr(self.ctype, self.op_name)
        
    @property
    def ctype(self):
        return cscience.datastore.sample_attributes.get_compare_type(self.key)

    def apply(self, s):
        try:
            val = self.ctype(s[self.key])
        except TypeError:
            print s[self.key]
            print self.ctype
            return False
        else:
            result = self.operation(val, self.value)
            return False if result == NotImplemented else result
    def copy(self):
        return FilterItem(self.key, self.op_name, self.value)
    @property
    def description(self):
        return ' '.join((self.key, self.show_op, self.show_value))
    def depends_on(self, filter_name):
        return False


class Filter(DataObject, list):

    def __init__(self, name, combinator=all, values=[]):
        self.name = name
        self.filter_func = combinator
        super(Filter, self).__init__(values)

    def apply(self, s):
        return not self or self.filter_func(itertools.imap(
                            lambda item, sample: item.apply(sample), 
                                        self, itertools.repeat(s)))
        
    @classmethod
    def make_plan_filter(cls, plan_name):
        newfilter = cls('Plan "%s"' % plan_name)
        newfilter.append(FilterItem(key='computation plan', op='__eq__', value=plan_name))
        return newfilter
        
    @property
    def filtertype(self):
        return self.filter_func.__name__.capitalize()
    @filtertype.setter
    def filtertype(self, value):
        self.filter_func = __builtins__[value.lower()]

    def copy(self):
        return Filter(str(self.name), self.filter_func, [item.copy() for item in self])
    @property        
    def description(self):
        return "Match %s: [%s]" % (self.filtertype, 
                '; '.join([item.description for item in self]))
    def depends_on(self, filter_name):
        return any([item.depends_on(filter_name) for item in self])        
    

class Filters(Collection):
    _tablename = 'filters'
    _itemtype = Filter
    
    def rename(self, oldname, newitem):
        #TODO: make deletion actually go to the db!
        #this currently works *only* for a not-previously-saved filter. Should
        #either fix this or fix the filter-creation workflow!
        del self._data[oldname]
        self[newitem.name] = newitem
        #TODO: make dependencies actually update!
        #for f in self._data.itervalues():
        #    for item in f:
        #        if item and item.depends_on(oldname):
        #            item.filter = newitem


forced_view = ('depth', 'computation plan')
len_forced = len(forced_view)
#TODO -- this ought to be handled a little more elegantly w/ a metaclass...
def force_index(fname):
    def inner(self, index=-1, *args, **kwargs):
        if index < 0:
            index = len(self) + index
        if index < len_forced:
            raise IndexError('Cannot delete required view attributes')
        return getattr(super(View, self), fname)(index, *args, **kwargs)
    return inner
class View(DataObject, list):
    
    def __init__(self, name="DEFAULT"):
        self.name = name
        super(View, self).__init__(forced_view) 
        
    def reverse(self):
        raise ValueError('View order is immutable')
    def sort(self):   
        raise ValueError('View order is immutable')
    #TODO: this probably ought to do something about delslice as well?
    __delitem__ = force_index('__delitem__')
    insert = force_index('insert')
    pop = force_index('pop')
    def remove(self, value):
        if value in forced_view:
            raise ValueError('Cannot delete required view attributes')
        return super(View, self).remove(value)
    def __contains__(self, item):
        """
        Wrapper so we can ask if an attribute or its name is in the view, for
        convenience.
        """
        return super(View, self).__contains__(getattr(item, 'name', item))
        
        
class AllView(DataObject):
    name = 'All'
    
    def __iter__(self):
        return iter(cscience.datastore.sample_attributes.sorted_keys)        
    def __getitem__(self, index):
        return cscience.datastore.sample_attributes.sorted_keys[index]
    def __len__(self):
        return len(cscience.datastore.sample_attributes)
    def __contains__(self, item):
        return getattr(item, 'name', item) in cscience.datastore.sample_attributes

class DefaultView(DataObject):
    name = 'Default'
    
    def _no_children_filter(self, item):
        return cscience.datastore.sample_attributes[item].parent is None
    
    def __iter__(self):
        return iter(filter(self._no_children_filter, cscience.datastore.sample_attributes.sorted_keys))
                
    def __getitem__(self, index):
        return filter(self._no_children_filter, cscience.datastore.sample_attributes.sorted_keys)[index]
    def __len__(self):
        return len(filter(self._no_children_filter, cscience.datastore.sample_attributes.sorted_keys))
    def __contains__(self, item):
        return getattr(item, 'name', item) in filter(self._no_children_filter, cscience.datastore.sample_attributes.sorted_keys)
        
class Views(Collection):
    _tablename = 'views'
    _itemtype = View

    def __iter__(self):
        yield 'Default'
        for key in sorted(self.keys()):
            if key != 'Default':
                yield key
    
    @classmethod
    def bootstrap(cls, connection):
        instance = super(Views, cls).bootstrap(connection)
        
        instance['Default'] = DefaultView()
        instance['All'] = AllView()
        
        return instance

