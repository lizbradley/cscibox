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

import collections
import itertools

import cscience.datastore
from cscience.framework.samples.attributes import _types
from cscience.framework import Collection

class TemplateField(object):
    #TODO: add units?

    def __init__(self, name, field_type='float', iskey=False):
        self.name = name
        self.field_type = field_type
        self.iskey = iskey

class Template(collections.OrderedDict):
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

        milieu.sortedkeys = sorted(milieu.keys())
        milieu.loaded = True
        return milieu

class Templates(Collection):
    _tablename = 'templates'

class Milieu(Collection):
    _tablename = 'milieus'

    @classmethod
    def connect(cls, backend):
        cls._table = backend.mtable(cls.tablename())

    def __init__(self, template, name='[NONE]', keyset=[]):
        self.name = name
        self.loaded = False
        try:
            self._template = template.name
        except AttributeError:
            self._template = template
        keyset = [tuple(item) for item in keyset]
        super(Milieu, self).__init__(keyset)
        self.sortedkeys = keyset

    def preload(self):
        if not self.loaded:
            self._forceload()

    def _forceload(self):
        for key, val in self._table.iter_milieu_data(self):
            self._data[key] = self._table.loaddictformat(val)
        self.sortedkeys = sorted(self.keys())
        self.loaded = True

    def saveitem(self, key, value):
        return (key, self._table.formatsavedict(value))

    def iteritems(self):
        self.preload()
        for key in self.sortedkeys:
            yield (key, self._data[key])

    def itervalues(self):
        for key, val in self.iteritems():
            val.update(dict(itertools.izip(self.template.key_fields, key)))
            yield val

    @property
    def template(self):
        return cscience.datastore.Datastore().templates[self._template]


class Milieus(Collection):
    _tablename = 'milieu_map'

    @classmethod
    def connect(cls, backend):
        cls._table = backend.maptable(cls.tablename(), Milieu.tablename())

    @classmethod
    def loadkeys(cls, backend):
        try:
            data = cls._table.loadkeys()
        except NameError:
            cls.instance = cls.bootstrap(backend)
        else:
            instance = cls([])
            Milieu.connect(backend)
            for key, value in data.iteritems():
                instance[key] = Milieu(value['template'], key, value.get('keys', []))

            cls.instance = instance

    def saveitem(self, key, value):
        return (key, self._table.formatsavedict({'template':value._template,
                                                 'keys':sorted(value.keys())}))
    def save(self, *args, **kwargs):
        super(Milieus, self).save(*args, **kwargs)
        for milieu in self._data.itervalues():
            kwargs['name'] = milieu.name
            milieu.save(*args, **kwargs)

