"""
Workflows.py

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

from ACE.Framework import Workflow

class Workflows(object):

    def __init__(self):
        self.workflows = {}

    def __str__(self):
        return '{workflows : %s}' % (self.workflows)

    __repr__ = __str__

    def add(self, workflow):
        self.workflows[workflow.get_name()] = workflow

    def remove(self, name):
        del self.workflows[name]

    def get(self, name):
        return self.workflows[name]

    def names(self):
        return sorted(self.workflows.keys())

    def save(self, path):
        workflows_path =  os.path.join(path, "workflows")

        if not os.path.exists(workflows_path):
            os.mkdir(workflows_path)

        keys = self.names()

        # delete workflows no longer in self.workflows()
        items = os.listdir(workflows_path)
        to_delete = [file for file in items if not file[0:len(file)-4] in keys]
        for file in to_delete:
            # skip invisible Unix directories like ".svn"
            if file.startswith("."):
                continue
            os.remove(os.path.join(workflows_path, file))

        for name in keys:
            workflow = self.get(name)
            workflow.save(workflows_path)

    def load(self, path):
        workflows_path =  os.path.join(path, "workflows")

        if not os.path.exists(workflows_path):
            os.mkdir(workflows_path)

        items   = os.listdir(workflows_path)
        workflows = [item for item in items if item.endswith('.txt')]
        for name in workflows:
            workflow = Workflow(name[0:len(name)-4], None)
            workflow.load(os.path.join(workflows_path, name))
            self.add(workflow)
