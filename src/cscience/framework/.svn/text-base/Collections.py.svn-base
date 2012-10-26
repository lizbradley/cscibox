"""
Collections.py

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

class Collections(object):

    def __init__(self):
        self.collections = {}

    def __str__(self):
        return '%s' % (self.collections)

    __repr__ = __str__

    def add(self, name, template, collection):
        self.collections[name] = [template,collection]
        
    def contains(self, name):
        return name in self.collections.keys()

    def remove(self, name):
        del(self.collections[name])

    def get(self, name):
        return self.collections[name][1]

    def get_template(self, name):
        return self.collections[name][0]

    def names(self):
        return sorted(self.collections.keys())

    def save(self, path):
        collections_path =  os.path.join(path, 'collections')

        if not os.path.exists(collections_path):
            os.mkdir(collections_path)

        collection_names = self.names()

        # delete collections no longer in self.collections
        items = os.listdir(collections_path)
        to_delete = [old_file for old_file in items if not old_file[0:len(old_file)-4] in items]
        for old_file in to_delete:
            # skip invisible Unix directories like ".svn"
            if old_file.startswith("."):
                continue
            file_path = os.path.join(collections_path, old_file)
            os.remove(file_path)

        for name in collection_names:
            collection = self.get(name)
            template   = self.get_template(name)
            output_file = file(os.path.join(collections_path,name + ".txt"), "w")
            output_file.write(template)
            output_file.write(os.linesep)
            output_file.write(repr(collection))
            output_file.write(os.linesep)
            output_file.flush()
            output_file.close()

    def load(self, path):
        collections_path =  os.path.join(path, 'collections')

        if not os.path.exists(collections_path):
            os.mkdir(collections_path)

        items = os.listdir(collections_path)
        files = [item for item in items if item.endswith('.txt')]
        for input_file in files:
            f = open(os.path.join(collections_path,input_file), "U")
            template = f.readline().strip()
            data = f.read()
            f.close()
            collection = eval(data)
            self.add(input_file[0:len(input_file)-4], template, collection)
