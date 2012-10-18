"""
FilterGroup.py

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

class FilterGroup(object):

    def __init__(self, group, isMember, repoman):
        self.group    = group
        self.isMember = isMember
        self.repoman  = repoman

    def apply(self, s):
        try:
            groups = self.repoman.GetModel('Groups')
            group = groups.get(self.group)
            return group.is_member(s['id'], s.nuclide) == self.isMember
        except:
            return False

    def save(self, f):
        f.write('BEGIN GROUP')
        f.write(os.linesep)
        f.write(self.group)
        f.write(os.linesep)
        f.write(repr(self.isMember))
        f.write(os.linesep)
        f.write('END GROUP')
        f.write(os.linesep)

    def copy(self):
        return FilterGroup(self.group, eval(repr(self.isMember)), self.repoman)

    def description(self):
        if self.isMember:
            return "IS MEMBER OF " + self.group
        else:
            return "IS NOT A MEMBER OF " + self.group

    def depends_on(self, filter_name):
        return False