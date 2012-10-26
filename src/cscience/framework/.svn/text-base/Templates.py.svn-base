"""
Templates.py

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

from ACE.Framework.Template import Template

class Templates(object):

    def __init__(self):
        self.templates = {}

    def add(self, template):
        self.templates[template.get_name()] = template

    def contains(self, name):
        return name in self.templates
        
    def get(self, name):
        return self.templates[name]
        
    def remove(self, name):
        del self.templates[name]

    def names(self):
        names = self.templates.keys()
        names.sort()
        return names
        
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
        templates_path = os.path.join(path, 'templates.txt')
        templates_file = open(templates_path, "U")

        lines = templates_file.readlines()

        templates_file.close()

        lines = [line.strip() for line in lines]
        lines = [line for line in lines if line != '']

        while len(lines) > 0:
            try:
                begin_index = lines.index('BEGIN TEMPLATE')
                end_index   = lines.index('END TEMPLATE')
                template = Template()
                template.load(lines[begin_index+1:end_index])
                self.add(template)
                del lines[begin_index:end_index+1]
            except:
                pass
