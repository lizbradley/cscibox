"""
views.py

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

class View(object):
    
    def __init__(self, name="DEFAULT"):
        self.name = name
        self.view_atts = []
        
    def __contains__(self, key):
        return key in self.view_atts

    def add(self, att):
        if att not in self.view_atts:
            self.view_atts.append(att)

    def name(self):
        return self.name

    def remove(self, att):
        self.view_atts.remove(att)
        
    def atts(self):
        return self.view_atts[:]

    def save(self, f):
        f.write(self.name)
        f.write(os.linesep)
        f.write('BEGIN ATTS')
        f.write(os.linesep)
        for att in self.view_atts:
            f.write(att)
            f.write(os.linesep)
        f.write('END ATTS')
        f.write(os.linesep)
        
class Views(object):

    def __init__(self):
        self.views = {'All':View('All')}

    def __contains__(self, key):
        return key in self.views

    def add(self, view):
        self.views[view.name] = view

    def get(self, name):
        return self.views[name]
        
    def remove(self, name):
        del self.views[name]

    def names(self):
        return sorted(self.views)
        
    def save(self, path):
        views_path = os.path.join(path, 'views.txt')
        views_file = open(views_path, "w")

        for name in self.names():
            view = self.get(name)
            views_file.write('BEGIN VIEW')
            views_file.write(os.linesep)
            view.save(views_file)
            views_file.write('END VIEW')
            views_file.write(os.linesep)
        
        views_file.flush()
        views_file.close()
    
    def load(self, path):
        print "loading views"
        views_path = os.path.join(path, 'views.txt')
        views_file = open(views_path, "U")

        lines = views_file.readlines()
        views_file.close()

        lines = [line.strip() for line in lines]
        lines = [line for line in lines if line]

        while lines:
            try:
                begin_index = lines.index('BEGIN VIEW')
                end_index = lines.index('END ATTS')
                view = View(lines[begin_index + 1])
                for i in range(begin_index + 3, end_index):
                    view.add(lines[i])
                self.add(view)
                del lines[begin_index:end_index + 2]
            except:
                pass
        print "views loaded"
