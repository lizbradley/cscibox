#!/usr/bin/env python

import cscience
from cscience import datastore
from cscience import framework

from cscience import backends
    
modelclasses = [framework.Attributes,  
                framework.Templates, 
                framework.Workflows, framework.ComputationPlans,
                framework.Filters, framework.Views]
instances = []
    
    
def load_old_data(loc):
    print 'loading repo data from hbase server'
    datastore.set_data_source(backends.hbase, loc)
    
    
    instance = datastore.cores
    for key in instance:
        core = instance[key]
        for depth in core:
            pass
    instances.append(instance)

    instance = datastore.milieus
    for key in instance:
        mil = instance[key]
        mil.preload()
    instances.append(instance)
    
    
    for mname in ('sample_attributes', 'templates', 
                  'workflows', 'computation_plans',
                  'filters', 'views'):
        instance = getattr(datastore, mname)
        for key in instance:
            #side effect loads the thing
            instance.get(key)
        instances.append(instance)
        
        
    print 'all data probably loaded...'

        
def save_new_data(loc):
    conn = backends.mongodb.Database(loc)
    framework.Milieu.connect(conn)
    framework.Core.connect(conn)
    for instance in instances:
        print 'saving new repo data for', instance.__class__.__name__
        try:
            instance.connect(conn)
            instance.bootstrap(conn)
        except:
            #table probably already exists. Oh wells.
            pass
        instance.save()


if __name__ == '__main__':
    load_old_data('ec2-54-201-157-21.us-west-2.compute.amazonaws.com')
    save_new_data('localhost')
    print 'success!'
    
    
    