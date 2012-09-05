"""
Filter.py

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

def And(a,b):
    return a and b

def Or(a,b):
    return a or b

def Apply(item, sample):
    return item.apply(sample)

class Filter(object):

    def __init__(self, name, combinator):
        self.items       = []
        self.filter_name = name
        self.filter      = combinator

    def apply(self, s):
        if len(self.items) == 0:
            return False
        samples = [s for item in self.items]
        results = map(Apply, self.items, samples)
        return reduce(self.filter, results) 

    def add_item(self, item):
        self.items.append(item)
        
    def remove_item(self, item):
        try:
            self.items.remove(item)
        except:
            pass
        
    def label(self):
        if self.filter == And:
            return "All"
        else:
            return "Any"

    def name(self):
        return self.filter_name

    def save(self, f):
        f.write(self.filter_name)
        f.write(os.linesep)
        if self.filter == And:
            f.write('And')
        else:
            f.write('Or')
        f.write(os.linesep)
        f.write('BEGIN ITEMS')
        f.write(os.linesep)
        for item in self.items:
             item.save(f)
        f.write('END ITEMS')
        f.write(os.linesep)
        
    def copy(self):
        new_filter = Filter(str(self.filter_name), self.filter)
        for item in self.items:
            new_filter.add_item(item.copy())
        return new_filter
        
    def description(self):
        desc = ""
        if self.filter == And:
            desc += "Match All: ["
        else:
            desc += "Match Any: ["
        for item in self.items:
            desc += item.description()
            desc += "; "
        # delete the space after the last semicolon
        if len(self.items) > 0:
            desc = desc[0:-1]
        desc += "]"
        return desc
        
    def depends_on(self, filter_name):
        for item in self.items:
            if item.depends_on(filter_name):
                return True
        return False
