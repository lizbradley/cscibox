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
from cscience.framework import Collection


forced_view = ('depth', 'run')
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
class View(list):

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


class AllView(object):
    name = 'All'

    def __iter__(self):
        return iter(cscience.datastore.Datastore().sample_attributes.sorted_keys)
    def __getitem__(self, index):
        return cscience.datastore.Datastore().sample_attributes.sorted_keys[index]
    def __len__(self):
        return len(cscience.datastore.Datastore().sample_attributes)
    def __contains__(self, item):
        return getattr(item, 'name', item) in cscience.datastore.Datastore().sample_attributes

allview = AllView()

class Views(Collection):
    _tablename = 'views'

    def __getitem__(self, name):
        if name == 'All':
            return allview
        else:
            return super(Views, self).__getitem__(name)

    def keys(self):
        return ['All'] + super(Views, self).keys()

    def __contains__(self, name):
        return name == 'All' or super(Views, self).__contains__(name)

    def __iter__(self):
        yield 'All'
        for key in sorted(self.keys()):
            yield key
