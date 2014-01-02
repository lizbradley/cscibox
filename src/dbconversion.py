#!/usr/bin/env python

import happybase
import os
import sys
import cPickle

from cscience import datastore
    
oldfiles = ['atts', 'cores', 'cplans', 'filters', 
            'milieus', 'templates', 'views', 'workflows']
instances = []
    
    
def load_old_data(path):
    for filename in oldfiles:
        my_file = os.path.join(path, os.extsep.join((filename, 'csc')))
        print 'loading old repo data from', my_file
        with open(my_file, 'rb') as repofile:
            instance = cPickle.load(repofile)
        instance.__class__.instance = instance #lulz
        instances.append(instance)
        
        
def save_new_data(connection):
    for instance in instances:
        print 'saving new repo data for', instance.__class__.__name__
        try:
            instance.bootstrap(connection)
        except:
            #table probably already exists. Oh wells.
            pass
        instance.save(connection)


if __name__ == '__main__':
    path = sys.argv[1]
    conn = happybase.Connection('ec2-54-201-224-16.us-west-2.compute.amazonaws.com')
    load_old_data(path)
    save_new_data(conn)
    print 'success!'
    
    
    