"""
datastore.py

* Copyright (c) 2012-2015, University of Colorado.
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

This module holds and manages instances of the objects used to access 
data storage for CScience.
"""

import sys
from cscience import framework


class Datastore(object):
    #TODO: do we care about posting changes to modified status to anywhere?
    data_modified = False
    data_source = ''
    
    models = {'sample_attributes':framework.Attributes, 
              'sample_db':framework.Samples, 
              'sample_groups':framework.Groups, 
              'templates':framework.Templates, 
              'milieus':framework.Milieus,
              'selectors':framework.Selectors, 
              'workflows':framework.Workflows, 
              'computation_plans':framework.ComputationPlans,
              'filters':framework.Filters, 
              'views':framework.Views}
    
   
    def set_data_source(self, source):
        """
        Set the source for repository data and do any appropriate initialization.
        """
        #NOTE: at this time, source is simply a directory name and all data is
        #effectively kept in main memory during program operation. Therefore, this
        #method currently loads all data into main memory from the given directory.
        #HOWEVER, this data model is not guaranteed, so this might change!
        self.data_source = source

        for model_name, model_class in self.models.iteritems():
            setattr(self, model_name, model_class.load(source))
        self.data_modified = False
        
    def save_datastore(self):
        for model_name in self.models:
            getattr(self, model_name).save(self.data_source)
        self.data_modified = False
    
    class RepositoryException(Exception): pass

sys.modules[__name__] = Datastore()

