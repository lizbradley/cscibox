"""
Nuclides.py

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

from ACE.Framework import Nuclide

class Nuclides(object):

    def __init__(self):
        self.nuclides = {}
        default_nuclide = Nuclide('ALL')
        self.add(default_nuclide)

    def add(self, nuclide):
        self.nuclides[nuclide.name()] = nuclide

    def contains(self, name):
        return name in self.nuclides
        
    def get(self, name):
        return self.nuclides[name]
        
    def remove(self, name):
        del self.nuclides[name]

    def names(self):
        return sorted(self.nuclides.keys())
        
    def save(self, path):
        nuclides_path = os.path.join(path, 'nuclides.txt')
        nuclides_file = open(nuclides_path, "w")

        for name in self.names():
            nuclide      = self.get(name)
            nuclides_file.write('BEGIN NUCLIDE')
            nuclides_file.write(os.linesep)
            nuclide.save(nuclides_file)
            nuclides_file.write('END NUCLIDE')
            nuclides_file.write(os.linesep)
        
        nuclides_file.flush()
        nuclides_file.close()

    def load(self, path):
        nuclides_path = os.path.join(path, 'nuclides.txt')
        nuclides_file = open(nuclides_path, "U")

        lines = nuclides_file.readlines()

        nuclides_file.close()

        lines = [line.strip() for line in lines]
        lines = [line for line in lines if line != '']

        while len(lines) > 0:
            try:
                begin_index  = lines.index('BEGIN NUCLIDE')
                end_required = lines.index('END REQUIRED')
                end_optional = lines.index('END OPTIONAL')
                nuclide = Nuclide(lines[begin_index+1])
                for i in range(begin_index+3, end_required):
                    nuclide.add_required(lines[i])
                for i in range(end_required+2, end_optional):
                    nuclide.add_optional(lines[i])
                self.add(nuclide)
                del lines[begin_index:end_optional+2]
            except:
                pass
