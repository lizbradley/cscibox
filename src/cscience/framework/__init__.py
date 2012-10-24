"""
__init__.py

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
import cPickle

class Collection(dict):
    """
    Base class for storing any given collection of CScience data types.
    Has methods for adding a new object, saving, and loading. 
    """
    
    _is_loaded = False
        
    def add(self, member):
        self[member.name] = member
        
    @classmethod
    def filename(cls):
        return os.extsep.join((cls._filename, 'csc'))
    @classmethod
    def default_instance(cls):
        return cls()
        
    def save(self, repopath):
        my_file_name = os.path.join(repopath, self.filename())
        with open(my_file_name, 'wb') as repofile:
            cPickle.dump(self, repofile, cPickle.HIGHEST_PROTOCOL)
            
    @classmethod
    def load(cls, repopath):
        """
        Load this Collection from repopath
        
        NOTE: To be made lazy!
        """
        if not cls._is_loaded:
            my_file_name = os.path.join(repopath, cls.filename())
            try:
                print cls, cls.__name__
                with open(my_file_name, 'rb') as repofile:
                    cls.instance = cPickle.load(repofile)
            except IOError:
                cls.instance = cls.default_instance()
            cls._is_loaded = True
        return cls.instance
        
from calculations import ComputationPlan, ComputationPlans, Workflow, \
    Workflows, Selector, Selectors
from paleobase import Milieu, Milieus, Template, Templates
from samples import Attribute, Attributes, Group, Groups, Sample, Samples, VirtualSample
from views import Filter, FilterFilter, FilterGroup, FilterItem, Filters, View, Views

__all__ = ('Attribute', 'Attributes', 'Milieu', 'Milieus', 'ComputationPlan', 'ComputationPlans', 
           'Selector', 'Selectors', 'Filter', 'FilterFilter', 'FilterGroup', 'FilterItem', 
           'Filters', 'Group', 'Groups', 'Sample', 'Samples', 'Template', 'Templates', 
           'View', 'Views', 'VirtualSample', 'Workflow', 'Workflows')
