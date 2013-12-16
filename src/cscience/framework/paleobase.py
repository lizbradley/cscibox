"""
collections.py

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

import cPickle
import collections
import itertools

import cscience.datastore
from cscience.framework.samples import _types
from cscience.framework import Collection, DataObject, DictDataDummy

class TemplateField(object):
    #TODO: add units?
    
    def __init__(self, name, field_type='float', iskey=False):
        self.name = name
        self.field_type = field_type
        self.iskey = iskey

class Template(DataObject, collections.OrderedDict):
    #TODO: allow unkeyed milieus
    """
    A Template defines the format of a Milieu for loading from csv files/
    required attribute checking/etc.
    """

    def __init__(self, *args, **kwargs):
        self.name = kwargs.pop('name', '[NONE]')
        self.key_fields = []
        super(Template, self).__init__(*args, **kwargs)
        
    def __iter__(self):
        for key in self.key_fields:
            yield key
        for key in self.iter_nonkeys():
            yield key
                
    def getitemat(self, index):
        return self.values()[index]
    
    def iter_nonkeys(self):
        for key in super(Template, self).__iter__():
            if key not in self.key_fields:
                yield key

    def add_field(self, name, field_type, iskey=False):
        self[name] = TemplateField(name, field_type, iskey)

    def __setitem__(self, key, value):
        super(Template, self).__setitem__(key, value)
        if value.iskey:
            if key not in self.key_fields:
                self.key_fields.append(key)
        elif key in self.key_fields:
            self.key_fields.remove(value)
            
    def __delitem__(self, key, *args, **kwargs):
        super(Template, self).__delitem__(key, *args, **kwargs)
        try:
            self.key_fields.remove(key)
        except ValueError:
            pass
        
    def new_milieu(self, dictm):
        """This method accepts a dictionary and returns a Milieu
        loaded using this template from that dictionary:
         -the template's key attributes are used as a key in the Milieu
         -all remaining template attributes are stored as the values in the
         Milieu. See the Milieu documentation for further details.
        """
        
        if not self or len(self) < 2:
            #can't have a milieu with only one column (or no columns)
            raise ValueError()
        
        def convert_field(field, value):
            if value is None or value == '':
                return None
            tp = _types[field.field_type]
            try:
                return tp(value)
            except ValueError:
                #sometimes things we want to import as ints are expressed as
                #floats in the original source -- this fixes that issue
                return tp(float(value))
            
        if self.key_fields:
            def makekey(index, row):
                return tuple([convert_field(self[key], row[key]) 
                            for key in self.key_fields])
        else:
            def makekey(index, row):
                return (index,)
            
        milieu = Milieu(self)
        for index, row in enumerate(dictm):
            keyval = makekey(index, row)         
            try:
                milieu[keyval] = dict([(att, convert_field(self[att], row[att])) 
                                       for att in self.iter_nonkeys()])   
            except:
                print row, keyval
                for att in self.iter_nonkeys():
                    print self[att], row[att]
                raise
            
        return milieu
        
class Templates(Collection):
    _tablename = 'templates'
    _itemtype = Template

class Milieu(Collection):
    _tablename = 'milieus'
    _itemtype = DictDataDummy
        
    def __init__(self, template, name='[NONE]', keyset=[]):
        self.name = name
        try:
            self._template = template.name
        except AttributeError:
            self._template = template
        super(Milieu, self).__init__(keyset)
    
    def _dbkey(self, key):
        #TODO: this function needs to be a lot more error-tolerant (or at least
        #better about reporting what you've done wrong)
        if type(key) != type(()):
            key = (key,)
        #TODO: better string conversion here?
        return ':'.join((self.name, ':'.join([str(k) for k in key])))
    
    def _forceload(self, keys=None):
        if not keys:
            keys = self.keys()
        dbkeys = [self._dbkey(key) for key in keys]
        rowset = self._table.rows(dbkeys)
        for key, val in itertools.izip(keys, rowset):
            self._data[key] = self._itemtype.loaddata(val[1])
    
    def loaditem(self, key):
        return super(Milieu, self).loaditem(self._dbkey(key))
    def saveitem(self, key, value):
        return (self._dbkey(key), self._itemtype.savedata('m', value))
    def savedata(self):
        return {'m:template':self._template, 
           'm:keys':cPickle.dumps(sorted(self.keys()), cPickle.HIGHEST_PROTOCOL)}
   
    def load(self, connection):
        self.connect(connection)
    
    #Make sure to test these!
    def iteritems(self):
        dbkeys = [self._dbkey(key) for key in keys]
        rowset = self._table.rows(dbkeys)
        for key, val in itertools.izip(keys, rowset):
            value = self._itemtype.loaddata(val[1])
            self._data[key] = value     
            yield (key, value)
    def itervalues(self):
        for key, val in self.iteritems():
            val.update(dict(itertools.izip(self.template.key_fields, key)))
            yield val      
            
    @property
    def template(self):
        return cscience.datastore.templates[self._template]
            

class Milieus(Collection):
    _tablename = 'milieu_map'
    _itemtype = Milieu
    
    @classmethod
    def bootstrap(cls, connection):
        """
        By default, each collection is one table with one column family (called
        'm') with one version of each cell within that column family. To 
        override this behavior, overload the bootstrap method!
        """
        connection.create_table(cls._itemtype.tablename(), {'m':{'max_versions':1}})
        return super(Milieus, cls).bootstrap(connection)
    
    @classmethod
    def loadkeys(cls, connection):
        #get everything from the map table, since this will be a simple case of
        #creating an object for each instance, and then making sure said object
        #can load all its stuff.
        scanner = cls._table.scan()
        #make an instance of the class
        #set its keys to the correct set of keys
        try:
            data = dict(scanner)
        except IllegalArgument:
            cls.instance = cls.bootstrap(connection)
        else:
            instance = cls([])
            for key, value in data.iteritems():
                instance[key] = cls._itemtype(value['m:template'], key, 
                                              cPickle.loads(value['m:keys']))
                instance[key].load(connection)
                
            cls.instance = instance
            
    def save(self, connection):
        super(Milieus, self).save(connection)
        for milieu in self._data.itervalues():
            #TODO: would be nice to handle this as all one batch
            milieu.save(connection)
    
