import happybase
import os
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
    #temp -- make this user-provideable yo
    path = '/Users/silverrose/Calvin/repo'
    conn = happybase.Connection('localhost')
    load_old_data(path)
    save_new_data(conn)
    print 'success!'
    
    
    