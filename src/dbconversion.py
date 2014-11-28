#!/usr/bin/env python

import cscience
from cscience.datastore import Datastore
from cscience import framework

from cscience import backends
instances = []
datastore = Datastore()


def load_old_data(loc):
    print 'loading repo data from hbase server'
    datastore.set_data_source(backends.hbase, loc)


    """
    instance = datastore.cores
    for key in instance:
        core = instance[key]
        for depth in core:
            pass
    instances.append(instance)
    """

    instance = datastore.milieus
    for key in instance:
        mil = instance[key]
        mil.preload()
    instances.append(instance)

    """

    #clean up parent/child attributes of yuck.
    instance = datastore.sample_attributes
    for key in instance.keys():
        att = instance[key]
        if getattr(att, 'parent', None):
            del instance._data[key]
        else:
            #fix atts that didn't get children added but assuredly should have errors!
            if getattr(att, 'children', None) or att.name in ('Corrected 14C Age',
                                                              'Reservoir Correction',
                                                              'Reservoir age correction'):
                att.has_error = True
            else:
                att.has_error = False
            delattr(att, 'parent')
            delattr(att, 'children')
    instances.append(instance)


    for mname in ('templates',
                  'workflows', 'computation_plans',
                  'filters', 'views'):
        instance = getattr(datastore, mname)
        for key in instance:
            #side effect loads the thing
            instance.get(key)
        instances.append(instance)

    """

    print 'all data loaded...'


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



