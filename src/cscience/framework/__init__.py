"""
__init__.py

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
import os
import cPickle

#TODO: this is really a metaclass!
class Collection(object):
    """
    Base class for storing any given collection of CScience data types.
    Has methods for adding a new object, saving, and loading. 
    """
    #implemented as extending object instead of dict because some dict methods
    #would be bad to have here (e.g. values()).
    
    _is_loaded = False
    
    def __new__(cls, *args, **kwargs):
        instance = super(Collection, cls).__new__(cls, *args, **kwargs)
        instance._data = {}
        instance._updated = set()
        return instance
    
    def __init__(self, keyset):
        #cached/memoized data that's already been loaded once.
        #TODO: keep this cache a reasonable size when applicable!
        self._data = dict.fromkeys(keyset)
        #keep a list of what keys have been updated to make saving operations
        #more sane -- currently not used.
        self._updated = set()
        
    def __contains__(self, name):
        return name in self._data
    
    def __iter__(self):
        for key in self._data:
            yield key
            
    def __len__(self):
        return len(self._data)
    
    def loaditem(self, name):
        return self._table.row(name)
    def saveitem(self, key, value):
        return (key, value.savedata())
        
    def __getitem__(self, name):
        val = self._data[name]
        if val is None:
            stored = self.loaditem(name)
            if not stored:
                raise KeyError # this really shouldn't happen
            else:
                self._data[name] = self._itemtype.loaddata(stored)
                return self._data[name]
        return val
        
    def __setitem__(self, name, item):
        self._data[name] = item
        self._updated.add(name)
        
    def add(self, member):
        self[member.name] = member
        
    def get(self, name, default=None):
        try:
            return self[name]
        except KeyError:
            return default
        
    def keys(self):
        return self._data.keys()
        
    @classmethod
    def tablename(cls):
        return cls._tablename
    @classmethod
    def connect(cls, connection):
        cls._table = connection.table(cls.tablename())
    @classmethod
    def loadkeys(cls, connection):
        scanner = cls._table.scan(
                        filter=b'KeyOnlyFilter() AND FirstKeyOnlyFilter()')
        #make an instance of the class
        #set its keys to the correct set of keys
        try:
            keys = [key for key, empty in scanner]
        except IllegalArgument:
            cls.instance = cls.bootstrap(connection)
        else:
            cls.instance = cls(keys)
    @classmethod
    def bootstrap(cls, connection):
        """
        By default, each collection is one table with one column family (called
        'm') with one version of each cell within that column family. To 
        override this behavior, overload the bootstrap method!
        """
        #TODO: attributes and views are special (some other stuff might be too)
        connection.create_table(cls.tablename(), {'m':{'max_versions':1}})
        return cls([])
    
        
    def save(self, connection):
        #TODO: only save actually changed records; for now, we're just resaving
        #everything that's been in memory ever.
        #print self._data
        self.connect(connection)
        batch = self._table.batch()
        for key, value in filter(lambda x: x[1] is not None, self._data.items()):
            batch.put(*self.saveitem(key, value))
        batch.send()
        #currently no deletions are allowed, so this should work just fine.
            
    @classmethod
    def load(cls, connection):
        """
        Load this Collection from the established database connection,
        or, make a new storage space if none exists yet.
        """
        if not cls._is_loaded:
            cls.connect(connection)
            cls.loadkeys(connection)
            cls._is_loaded = True
        return cls.instance
    
class DataObject(object):
    """
    Default save & load operations for individual data objects to persistent
    storage.
    """
    
    def savedata(self):
        return {'m:data':cPickle.dumps(self, cPickle.HIGHEST_PROTOCOL)}
    @classmethod
    def loaddata(cls, data):
        return cPickle.loads(data['m:data'])
    
class DictDataDummy(object):
    """
    Save & load conversions for data stored as a dictionary of happiness in
    persistent storage
    """
    
    @classmethod
    def savedata(cls, colfam, data):
        return dict([('{}:{}'.format(colfam, key), 
                      cPickle.dumps(value, cPickle.HIGHEST_PROTOCOL)) 
                     for key, value in data.items()])
    
    @classmethod
    def loaddata(cls, data):
        return dict([(key.split(':', 1)[1], cPickle.loads(value)) 
                     for key, value in data.items()])
        
from calculations import ComputationPlan, ComputationPlans, Workflow, \
    Workflows, Selector, Selectors
from paleobase import Milieu, Milieus, Template, Templates
from samples import Attribute, Attributes, Core, VirtualCore, Cores, Sample
from samples import VirtualSample, UncertainQuantity, Uncertainty
from views import Filter, FilterFilter, FilterItem, Filters, View, Views

__all__ = ('Attribute', 'Attributes', 'Milieu', 'Milieus', 'ComputationPlan', 'ComputationPlans', 
           'Selector', 'Selectors', 'Filter', 'FilterFilter', 'FilterItem', 
           'Filters', 'Core', 'Cores', 'Sample', 'Template', 'Templates', 
           'View', 'Views', 'VirtualSample', 'Workflow', 'Workflows')
