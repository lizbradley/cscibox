#!/usr/bin/env python

import happybase
import pymongo
import framework


from cscience import datastore
    
modelclasses = [framework.Attributes, framework.Cores, 
                framework.Templates, framework.Milieus,
                framework.Workflows, framework.ComputationPlans,
                framework.Filters, framework.Views]
instances = []
    
    
def load_old_data(connection):
    print 'loading repo data from hbase server'
    for cls in modelclasses:
        instance = cls.load(connection)
        instances.append(instance)
        
def save_new_data(connection):
    for instance in instances:
        print 'saving new repo data for', instance.__class__.__name__
        try:
            instance.bootstrap(connection)
        except:
            #table probably already exists. Oh wells.
            pass
        instance.save()


if __name__ == '__main__':
    path = sys.argv[1]
    conn = happybase.Connection('ec2-54-201-224-16.us-west-2.compute.amazonaws.com')
    load_old_data(path)
    save_new_data(conn)
    print 'success!'
    
    
    