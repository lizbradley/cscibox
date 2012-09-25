"""
Filters.py

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

import os.path

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

class Filter(object):

    def __init__(self, name, combinator=all):
        self.items = []
        self.filter_name = name
        self.filter = combinator

    def apply(self, s):
        return self.items and self.filter(
                    map(lambda item, sample: item.apply(sample), 
                      self.items, [s] * len(self.items)))

    def add_item(self, item):
        self.items.append(item)
        
    def remove_item(self, item):
        try:
            self.items.remove(item)
        except ValueError:
            pass
        
    def label(self):
        return self.filter.__name__.capitalize()

    def name(self):
        return self.filter_name

    def save(self, f):
        f.write(self.filter_name)
        f.write(os.linesep)
        f.write(self.filter.__name__)
        f.write(os.linesep)
        f.write('BEGIN ITEMS')
        f.write(os.linesep)
        for item in self.items:
            item.save(f)
        f.write('END ITEMS')
        f.write(os.linesep)
        
    def copy(self):
        new_filter = Filter(str(self.filter_name), self.filter)
        for item in self.items:
            new_filter.add_item(item.copy())
        return new_filter
        
    def description(self):
        return "Match %s: [%s]" % (self.label(), 
                '; '.join([item.description for item in self.items]))
        
    def depends_on(self, filter_name):
        return any([item.depends_on(filter_name) for item in self.items])
    
class FilterFilter(object):
    """
    Used for negating an existing Filter
    """

    def __init__(self, internal_filter, value=True):
        self.filter = internal_filter
        self.value = bool(value)

    def apply(self, s):
        return self.filter.apply(s) == self.value

    def save(self, f):
        f.write('BEGIN FILTERFILTER')
        f.write(os.linesep)
        f.write(self.filter.name())
        f.write(os.linesep)
        f.write(repr(self.value))
        f.write(os.linesep)
        f.write('END FILTERFILTER')
        f.write(os.linesep)

    def copy(self):
        return FilterFilter(self.filter, self.value)
    def description(self):
        return self.value and self.filter.description() or \
                "NOT (%s)" % self.filter.description()
    def depends_on(self, filter_name):
        return self.filter.name() == filter_name
    

class FilterGroup(object):

    def __init__(self, group, is_member, repoman):
        self.group = group
        self.is_member = bool(is_member)
        self.repoman = repoman

    def apply(self, s):
        groups = self.repoman.GetModel('Groups')
        group = groups.get(self.group)
        return groups.get(self.group).is_member(s['id']) == self.isMember

    def save(self, f):
        f.write('BEGIN GROUP')
        f.write(os.linesep)
        f.write(self.group)
        f.write(os.linesep)
        f.write(repr(self.is_member))
        f.write(os.linesep)
        f.write('END GROUP')
        f.write(os.linesep)

    def copy(self):
        return FilterGroup(self.group, self.is_member, self.repoman)
    def description(self):
        return 'IS%s MEMBER OF %s' % (self.is_member and '' or ' NOT A', self.group)
    def depends_on(self, filter_name):
        return False
    
class FilterItem(object):

    def __init__(self, key, op, value):
        self.key = key
        self.value = value
        self.op_name = op
        try:
            self.operation = getattr(self.value, op)
        except AttributeError:
            #ints and booleans don't have some of the useful comparison builtins,
            #but converting them to floats works.
            self.operation = getattr(float(self.value), op)

    def apply(self, s):
        result = self.operation(s[self.key])
        return result != NotImplemented and True or False

    def save(self, f):
        f.write('BEGIN ITEM')
        f.write(os.linesep)
        f.write(self.key)
        f.write(os.linesep)
        f.write(operation_name(self.op_name))
        f.write(os.linesep)
        f.write(repr(self.value))
        f.write(os.linesep)
        f.write('END ITEM')
        f.write(os.linesep)
        
    def copy(self):
        return FilterItem(self.key, self.op_name, self.value)
        
    def description(self):
        return ' '.join((self.key, operation_name(self.op_name), str(self.value)))

    def depends_on(self, filter_name):
        return False

class Filters(object):

    def __init__(self):
        self.filters = {}

    def add(self, filter):
        self.filters[filter.name()] = filter

    def contains(self, name):
        return name in self.filters
        
    def get(self, name):
        return self.filters[name]
        
    def remove(self, name):
        del self.filters[name]

    def names(self):
        return sorted(self.filters)
        
    def save(self, path):
        filters_path = os.path.join(path, 'filters.txt')
        filters_file = open(filters_path, "w")

        for name in self.names():
            filter = self.get(name)
            filters_file.write('BEGIN FILTER')
            filters_file.write(os.linesep)
            filter.save(filters_file)
            filters_file.write('END FILTER')
            filters_file.write(os.linesep)
        
        filters_file.flush()
        filters_file.close()

    def load(self, path, repoman):
        filters_path = os.path.join(path, 'filters.txt')
        filters_file = open(filters_path, "U")

        lines = filters_file.readlines()
        filters_file.close()

        lines = [line.strip() for line in lines]
        lines = [line for line in lines if line]

        # find out how many filters have been saved in the file
        # stick each individual filter in its own list
        filter_sets = []

        while lines:
            try:
                end_index = lines.index('END FILTER')
                filter_set = []
                i = 1
                while i < end_index:
                    filter_set.append(lines[i])
                    i += 1
                filter_sets.append(filter_set)
                del lines[0:end_index + 1]
            except:
                pass

        # some filters depend on other filters
        # the loop below makes sure that we don't
        # load a filter until all of the filters it depends on
        # have been loaded

        processed = []

        while len(filter_sets) > 0:
            filter_set = filter_sets.pop(0)
            index = 0
            names = []
            for line in filter_set:
                if line.endswith('BEGIN FILTERFILTER'):
                    names.append(filter_set[index + 1])
                index += 1
            total = 0
            for name in names:
                if name in processed:
                    total += 1
            if total == len(names):
                processed.append(filter_set[0])
                filter = self.create_filter(filter_set, repoman)
                self.add(filter)
            else:
                filter_sets.append(filter_set)

    def create_filter(self, filter_set, repoman):
        name = filter_set.pop(0)
        filter = Filter(name, __builtins__[filter_set.pop(0)])
        
        # Get rid of 'begin items' and 'end items' strings
        filter_set.pop(0)
        filter_set.pop()

        while filter_set:
            filter_type = filter_set.pop(0)
            if filter_type == "BEGIN ITEM":
                key = filter_set.pop(0)
                op = named_operation(filter_set.pop(0))
                value = eval(filter_set.pop(0))
                filter.add_item(FilterItem(key, op, value))
            elif filter_type == "BEGIN GROUP":
                group = filter_set.pop(0)
                isMember = eval(filter_set.pop(0))
                filter.add_item(FilterGroup(group, isMember, repoman))
            else:
                target = self.get(filter_set.pop(0))
                value = eval(filter_set.pop(0))
                filter.add_item(FilterFilter(target, value))
            # Get rid of 'end item', 'end group' or 'end filterfilter' strings
            filter_set.pop(0)

        return filter
