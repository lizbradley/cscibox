"""
Group.py

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

import copy
import os

class Group(object):
    
    def __init__(self, name):
        self.group_name = name
        self.samples = set()
        
    def __len__(self):
        return len(self.samples)

    def __contains__(self, member):
        return member in self.samples
        
    def add(self, s_id, nuclide):
        self.samples.add((s_id,nuclide))
        
    def add_member(self, member):
        self.samples.add(member)
        
    def duplicate(self, new_name):
        new_group = Group(new_name)
        new_group.samples = copy.deepcopy(self.samples)
        return new_group

    def is_member(self, s_id, nuclide):
        member = (s_id, nuclide)
        return member in self.samples

    def name(self):
        return self.group_name

    def remove(self, s_id, nuclide):
        self.samples.remove((s_id,nuclide))
        
    def members(self):
        return sorted(list(self.samples))
        
    def get_ids(self):
        ids = [item[0] for item in self.samples]
        ids = set(ids)
        return list(ids)
        
    def get_nuclides(self):
        nuclides = [item[1] for item in self.samples]
        nuclides = set(nuclides)
        return list(nuclides)
        
    def is_calibration_set(self, samples_db):
        
        if len(self.samples) == 0:
            return False
        
        nuclides = [item[1] for item in self.samples]
        nuclides = set(nuclides)
        
        # a calibration set must contain only one type of nuclide
        if len(nuclides) > 1:
            return False
        
        ids     = [item[0] for item in self.samples]
        samples = [samples_db.get(s_id) for s_id in ids]
        
        ages    = [sample['independent age'] for sample in samples]
        ages    = [item for item in ages if item is not None]
        
        # all samples in a calibration set must have the independent age attribute
        if len(ages) != len(self.samples):
            return False
            
        uncert  = [sample['independent age uncertainty'] for sample in samples]
        uncert  = [item for item in uncert if item is not None]
        
        # all samples in a calibration set must have the independent age uncertainty attribute
        if len(uncert) != len(self.samples):
            return False
            
        return True

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
