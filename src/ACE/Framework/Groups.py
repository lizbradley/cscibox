"""
groups.py

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
import copy

class Group(object):
    
    def __init__(self, name):
        self.name = name
        self.samples = set()
        
    def __len__(self):
        return len(self.samples)

    def __contains__(self, member):
        return member in self.samples
        
    def add(self, member):
        self.samples.add(member)
        
    def duplicate(self, new_name):
        new_group = Group(new_name)
        new_group.samples = copy.deepcopy(self.samples)
        return new_group

    def is_member(self, s_id):
        return s_id in self.samples

    def remove(self, s_id):
        self.samples.remove(s_id)
        
    def members(self):
        return sorted(list(self.samples))
        
    def save(self, f):
        f.write(self.group_name)
        f.write(os.linesep)
        f.write('BEGIN MEMBERS')
        f.write(os.linesep)
        for member in self.samples:
            f.write(repr(member))
            f.write(os.linesep)
        f.write('END MEMBERS')
        f.write(os.linesep)


class Groups(object):

    def __init__(self):
        self.groups = {}

    def __contains__(self, key):
        return key in self.groups

    def add(self, group):
        self.groups[group.name] = group
        
    def get(self, name):
        return self.groups[name]
        
    def remove(self, name):
        del self.groups[name]

    def names(self):
        return sorted(self.groups)
        
    def save(self, path):
        groups_path = os.path.join(path, 'groups.txt')
        groups_file = open(groups_path, "w")

        for name in self.names():
            group = self.get(name)
            groups_file.write('BEGIN GROUP')
            groups_file.write(os.linesep)
            group.save(groups_file)
            groups_file.write('END GROUP')
            groups_file.write(os.linesep)
        
        groups_file.flush()
        groups_file.close()
    
    def load(self, path):
        print "loading groups"
        groups_path = os.path.join(path, 'groups.txt')
        groups_file = open(groups_path, "U")

        lines = groups_file.readlines()
        groups_file.close()
        lines = [line.strip() for line in lines]
        lines = [line for line in lines if line]

        while lines:
            try:
                begin_index = lines.index('BEGIN GROUP')
                end_index = lines.index('END MEMBERS')
                group = Group(lines[begin_index + 1])
                for i in range(begin_index + 3, end_index):
                    group.add_member(eval(lines[i]))
                self.add(group)
                del lines[begin_index:end_index + 2]
            except:
                pass
        print "groups load done"
