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

import os
import os.path

import Filter
import Operations

from FilterItem   import FilterItem
from FilterGroup  import FilterGroup
from FilterFilter import FilterFilter

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
        return sorted(self.filters.keys())
        
    def save(self, path):
        filters_path = os.path.join(path, 'filters.txt')
        filters_file = open(filters_path, "w")

        for name in self.names():
            filter      = self.get(name)
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
        lines = [line for line in lines if line != '']

        # find out how many filters have been saved in the file
        # stick each individual filter in its own list
        filter_sets = []

        while len(lines) > 0:
            try:
                end_index = lines.index('END FILTER')
                filter_set = []
                i = 1
                while i < end_index:
                    filter_set.append(lines[i])
                    i += 1
                filter_sets.append(filter_set)
                del lines[0:end_index+1]
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
                    names.append(filter_set[index+1])
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
        filter = None
        name = filter_set.pop(0)
        if filter_set.pop(0) == "And":
            filter = Filter.Filter(name, Filter.And)
        else:
            filter = Filter.Filter(name, Filter.Or)

        # Get rid of 'begin items' and 'end items' strings
        filter_set.pop(0)
        filter_set.pop()

        while len(filter_set) > 0:
            filter_type = filter_set.pop(0)
            if filter_type == "BEGIN ITEM":
                key   = filter_set.pop(0)
                op    = Operations.opForName(filter_set.pop(0))
                value = eval(filter_set.pop(0))
                filter.add_item(FilterItem(key, op, value))
            elif filter_type == "BEGIN GROUP":
                group    = filter_set.pop(0)
                isMember =  eval(filter_set.pop(0))
                filter.add_item(FilterGroup(group, isMember, repoman))
            else:
                target = self.get(filter_set.pop(0))
                value  = eval(filter_set.pop(0))
                filter.add_item(FilterFilter(target, value))
            # Get rid of 'end item', 'end group' or 'end filterfilter' strings
            filter_set.pop(0)

        return filter
