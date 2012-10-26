"""
Workflow.py

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

from collections import deque
import imp

import ACE.Components

class Workflow(object):

    def __init__(self, name, workflowType):
        self.name        = name
        self.type        = workflowType
        self.dating      = None
        self.supported   = []
        self.connections = {}
        self.collections = None
        self.factors     = None
        self.nuclides    = None

    def __str__(self):
        return '{name : %s, connections : %s}' % (self.name, self.connections)

    __repr__ = __str__

    def add_supported_nuclide(self, nuclide):
        if not nuclide in self.supported:
            self.supported.append(nuclide)

    def remove_supported_nuclide(self, nuclide):
        if nuclide in self.supported:
            self.supported.remove(nuclide)

    def supports_nuclide(self, nuclide):
        return nuclide in self.supported

    def get_name(self):
        return self.name

    def get_type(self):
        return self.type

    def get_dating_workflow(self):
        return self.dating

    def load_component(self, name, experiment):
        # all components should come from ACE.Components
        # name = 'ACE.Components.' + name
        tup  = imp.find_module(name, ACE.Components.__path__)
        mod  = imp.load_module(name, *tup)
        comp = getattr(mod, name)
        instance = comp(self.collections, self)
        instance.set_experiment(experiment)
        return instance

    def components_for_factor(self, name, experiment):
        start  = name.find("<")
        end    = name.find(">")
        factor = name[start+1:end]
        mode   = experiment[factor]
        factor = self.factors.get(factor)
        return factor.get_components_for_mode(mode)

    def get_nuclides(self):
        return self.nuclides

    def get_factors(self):
        factors = []
        names = self.connections.keys()
        for name in names:
            if name.startswith("Factor"):
                start  = name.find("<")
                end    = name.find(">")
                factor = name[start+1:end]
                if not factor in factors:
                    factors.append(factor)
        return factors

    def instantiate(self, experiment):
       components = {}

       # load all components mentioned in workflow into memory
       # if component is a factor, retrieve the components
       # selected for this factor and load them as well
       names = self.connections.keys()
       for name in names:
           if name.startswith("Factor"):
               comps  = self.components_for_factor(name, experiment)
               for comp in comps:
                   components[comp] = self.load_component(comp, experiment)
           else:
               components[name] = self.load_component(name, experiment)

       # loop through all components and connect them up according to
       # the information stored in self.connections. Only factors
       # are particularly tricky. We need to check if a factor maps onto
       # more than one component. If so, we need to connect those components
       # together in the order specified, and then we need to hook up
       # the component prior to the factor to the factor's first component
       # and hook up the factor's last component to the component that
       # appears after the factor in the workflow
       for name in names:
           if name.startswith("Factor"):
               comps  = self.components_for_factor(name, experiment)
               if len(comps) > 1:
                   i = 0
                   while i < len(comps) - 1:
                       comp  = components[comps[i]]
                       tcomp = components[comps[i+1]]
                       comp.connect(tcomp)
                       i = i + 1
               comp = components[comps[-1]]
               connections = self.connections[name]
               ports       = connections.keys()
               for port in ports:
                   target  = connections[port]
                   if target.startswith("Factor"):
                       tcomps  = self.components_for_factor(target, experiment)
                       tcomp  = components[tcomps[0]]
                       comp.connect(tcomp, port)
                   else:
                       tcomp = components[target]
                       comp.connect(tcomp, port)
           else:
               comp        = components[name]
               connections = self.connections[name]
               ports       = connections.keys()
               for port in ports:
                   target  = connections[port]
                   if target.startswith("Factor"):
                       comps  = self.components_for_factor(target, experiment)
                       tcomp  = components[comps[0]]
                       comp.connect(tcomp, port)
                   else:
                       tcomp = components[target]
                       comp.connect(tcomp, port)

       return components
        
    def execute(self, experiment, samples, dialog, browser):
        
        self.dialog  = dialog
        self.browser = browser
        
        if self.factors != None:
            
            self.total_samples = len(samples)
            
            components = self.instantiate(experiment)

            first_component = components[self.find_first_component()]

            # bad ass pythonic execution algorithm written by Evan Sheehan
            # gist: 
            #       1. create a queue that contains a tuple of the first
            #          component of the workflow and the set of samples
            #          to process
            #       2. pull the first tuple off the queue, get its component
            #          and pass the set of samples to it. Note: components
            #          are 'callable' objects to enable this style of
            #          processing
            #       3. When a component is invoked, it processes the set of
            #          samples handed to it and returns a tuple of the next
            #          component to execute and the samples it needs to process
            #       4. This tuple gets added to the queue and we continue
            #          to invoke components and add tuples to the queue until
            #          the queue is empty.
            #       Note: we only add a tuple to the queue if it a) has greater
            #             than zero samples to process and 2) is not already in
            #             the queue. This ensures that the queue eventually
            #             empties out.
            q = deque([([first_component], samples)])
            while len(q) > 0:
                if self.dialog.cancel:
                    break
                components, samples = q.popleft()
                for pending in map(lambda comp: comp(samples), components):
                    for pair in pending:
                        if len(pair[1]) and pending not in q:
                            q.append(pair)
            del(self.total_samples)
            del(self.dialog)
            del(self.browser)

    def find_first_component(self):
        notFirst = []
        names = self.connections.keys()
        for name in names:
            mappings = self.connections[name]
            ports = mappings.keys()
            for port in ports:
                destination = mappings[port]
                if destination != None:
                    if not destination in notFirst:
                        notFirst.append(destination)
        first_comp = [name for name in names if not name in notFirst]
        if len(first_comp) == 1:
            return first_comp[0]
        raise Exception, "Workflow does not have a clear first component"

    def load(self, file):
        self.connections.clear()
        f = open(file, "U")
        self.type = f.readline().strip()
        self.dating = f.readline().strip()
        if self.dating == "":
            self.dating = None
        self.supported = eval(f.readline().strip())
        line = f.readline().strip()
        while line != "":
            index           = line.find("=>")
            source          = line[0:index-1]
            destination     = line[index+3:]

            port_index      = source.find(".")
            if port_index > 0:
                port   = source[port_index+1:]
                source = source[0:port_index]
            else:
                port   = 'output'

            if not self.connections.has_key(source):
                self.connections[source] = {}
            if not self.connections.has_key(destination):
                self.connections[destination] = {}

            mappings = self.connections[source]
            mappings[port] = destination

            line = f.readline().strip()
        f.close()
        
    def save(self, path):
        pass
    
    def set_collections(self, collections):
        self.collections = collections

    def set_factors(self, factors):
        self.factors = factors

    def set_nuclides(self, nuclides):
        self.nuclides = nuclides
        
    def set_dating_workflow(self, datingWorkflow):
        if datingWorkflow.get_type() == "dating":
            self.dating = datingWorkflow.get_name()
