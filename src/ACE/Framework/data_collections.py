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

import os.path
import csv

class Template(object):
    """
    A Template defines the format of a Collection for loading from csv files/
    required attribute checking/etc.
    """

    def __init__(self, name='[NONE]'):
        self.name = name
        self.fields = {}
        self.order = []
        self.keys = []

    def add_field(self, name, field_type):
        self.fields[name] = field_type
        if not name in self.order:
            self.order.append(name)

    def get_keys(self):
        return self.keys[:]

    def get_field_type(self, name):
        return self.fields[name]

    def get_name(self):
        return self.name

    def get_order(self):
        return self.order[:]

    def has_field(self, name):
        return name in self.order

    def move_down(self, index):
        name = self.order.pop(index)
        self.order.insert(index + 1, name)
        
    def move_up(self, index):
        name = self.order.pop(index)
        self.order.insert(index - 1, name)

    def names(self):
        return sorted(self.order)

    def remove_field(self, name):
        del self.fields[name]
        self.order.remove(name)
        if name in self.keys:
            self.keys.remove(name)
        
    def size(self):
        return len(self.order)

    def set_name(self, name):
        self.name = name

    def add_key(self, name):
        if name in self.order:
            if name not in self.keys:
                self.keys.append(name)

    def remove_key(self, name):
        if name in self.order:
            if name in self.keys:
                self.keys.remove(name)
    
    def convert_field(self, field_type, value):
        if field_type == "string":
            return str(value)
        elif field_type == "float":
            return float(value)
        else:
            return int(value)
        
    def new_collection(self, csv_file):
        """This method accepts a path to a .csv file and returns a dictionary 
            that has the following structure:
         -the template's key attributes are combined into a tuple and that tuple 
           is used as an index to the returned dictionary
         -all remaining template attributes are stored in a second dictionary 
           which is accessed by the above index
        There are two exceptions to the above rules:
         -If the template has only one key attribute, then that attribute is used 
           to index the returned dictionary directly
         -If the template has only one non-key attribute, then no second dictionary 
           is created and that attribute is instead accessed directly by the returned 
           dictionary's index
        The csv_file must point to a csv file that contains one field per attribute 
        defined in the template.
        If there is a problem with the .csv file, this method returns None.
        If the template has no key attributes, this method returns None.
        Finally, if the template has less than two fields, this method returns None."""
            
        keys = self.get_keys()
        
        if not keys:
            return None
        if self.size() < 2:
            return None
            
        collection = {}
        input_file = file(csv_file, "U")
        r = csv.DictReader(input_file, self.order)
        for row in r:
            if len(keys) == 1:
                key_value = self.convert_field(self.get_field_type(keys[0]), row[keys[0]])
            else:
                values = []
                for key in keys:
                    values.append(self.convert_field(self.get_field_type(key), row[key]))
                key_value = tuple(values)
                
            other_fields = self.names()
            for key in keys:
                other_fields.remove(key)
                
            if len(other_fields) == 1:
                att = other_fields[0]
                field_value = self.convert_field(self.get_field_type(att), row[att])
                collection[key_value] = field_value
            else:
                entry = {}
                for att in other_fields:
                    field_value = self.convert_field(self.get_field_type(att), row[att])
                    entry[att] = field_value
                collection[key_value] = entry
        return collection

    def save(self, f):
        if self.name is None:
            f.write("[NONE]")
        else:
            f.write(self.name)
        f.write(os.linesep)
        f.write(repr(self.fields))
        f.write(os.linesep)
        f.write(repr(self.order))
        f.write(os.linesep)
        f.write(repr(self.keys))
        f.write(os.linesep)

    def load(self, values):
        self.name = values[0]
        if self.name == "[NONE]":
            self.name = None
        self.fields = eval(values[1])
        self.order = eval(values[2])
        self.keys = eval(values[3])
        
        
class Templates(object):

    def __init__(self):
        self.templates = {}

    def add(self, template):
        self.templates[template.name] = template

    def contains(self, name):
        return name in self.templates
        
    def get(self, name):
        return self.templates[name]
        
    def remove(self, name):
        del self.templates[name]

    def names(self):
        return sorted(self.templates)
        
    def save(self, path):
        templates_path = os.path.join(path, 'templates.txt')
        templates_file = open(templates_path, "w")

        for name in self.names():
            template = self.get(name)
            templates_file.write('BEGIN TEMPLATE')
            templates_file.write(os.linesep)
            template.save(templates_file)
            templates_file.write('END TEMPLATE')
            templates_file.write(os.linesep)
        
        templates_file.flush()
        templates_file.close()
    
    def load(self, path):
        print "loading templates"
        templates_path = os.path.join(path, 'templates.txt')
        templates_file = open(templates_path, "U")

        lines = templates_file.readlines()
        templates_file.close()

        lines = [line.strip() for line in lines]
        lines = [line for line in lines if line]
        
        print lines

        while lines:
            try:
                begin_index = lines.index('BEGIN TEMPLATE')
                end_index = lines.index('END TEMPLATE')
                template = Template()
                template.load(lines[begin_index + 1:end_index])
                self.add(template)
                del lines[begin_index:end_index + 1]
            except Exception as e:
                pass
        print "templates loaded"


class Collections(object):

    def __init__(self):
        self.collections = {}

    def __str__(self):
        return str(self.collections)
    def __repr__(self):
        return repr(self.collections)

    def add(self, name, template, collection):
        self.collections[name] = [template, collection]
        
    def contains(self, name):
        return name in self.collections

    def remove(self, name):
        del self.collections[name]

    def get(self, name):
        return self.collections[name][1]

    def get_template(self, name):
        return self.collections[name][0]

    def names(self):
        return sorted(self.collections.keys())

    def save(self, path):
        collections_path = os.path.join(path, 'collections')
        if not os.path.exists(collections_path):
            os.mkdir(collections_path)
        collection_names = self.names()

        # delete collections no longer in self.collections
        items = os.listdir(collections_path)
        to_delete = [old_file for old_file in items if not old_file[0:len(old_file) - 4] in items]
        for old_file in to_delete:
            # skip invisible Unix directories like ".svn"
            if old_file.startswith("."):
                continue
            file_path = os.path.join(collections_path, old_file)
            os.remove(file_path)

        for name in collection_names:
            collection = self.get(name)
            template = self.get_template(name)
            output_file = file(os.path.join(collections_path, name + ".txt"), "w")
            output_file.write(template)
            output_file.write(os.linesep)
            output_file.write(repr(collection))
            output_file.write(os.linesep)
            output_file.flush()
            output_file.close()

    def load(self, path):
        collections_path = os.path.join(path, 'collections')
        if not os.path.exists(collections_path):
            os.mkdir(collections_path)

        items = os.listdir(collections_path)
        files = [item for item in items if item.endswith('.txt')]
        for input_file in files:
            f = open(os.path.join(collections_path, input_file), "U")
            template = f.readline().strip()
            data = f.read()
            f.close()
            collection = eval(data)
            self.add(input_file[0:-4], template, collection)
