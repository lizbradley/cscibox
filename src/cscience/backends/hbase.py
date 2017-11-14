import itertools

import happybase
import cPickle

class Database(object):
    
    def __init__(self, data_source, port):
        self.connection = happybase.Connection(data_source, port)
        
    def table(self, tablename):
        return Table(self.connection, tablename)
    
    def ctable(self, tablename):
        return CoreTable(self.connection, tablename)
    
    def mtable(self, tablename):
        return MilieuTable(self.connection, tablename)
        
    def maptable(self, maptablename, itemtablename):
        return MapTable(self.connection, maptablename, itemtablename)
        
class Table(object):
    _colfam = 'm'
    
    def __init__(self, connection, name):
        self.name = name
        self.connection = connection
        self.native_tbl = connection.table(name)
        
    def do_create(self):
        self.connection.create_table(self.name, {self._colfam:{'max_versions':1}})
        
    def loadone(self, key):
        return self.native_tbl.row(key)
    def savemany(self, items, *args, **kwargs):
        batch = self.native_tbl.batch()
        for key, value in items:
            batch.put(key, value)
        batch.send()
        #currently no deletions are allowed, so this should work just fine.
        
    def loadkeys(self):
        scanner = self.native_tbl.scan(
                        filter=b'KeyOnlyFilter() AND FirstKeyOnlyFilter()')
        #make an instance of the class
        #set its keys to the correct set of keys
        try:
            return [key for key, empty in scanner]
        except happybase.hbase.ttypes.IllegalArgument:
            raise NameError
        
        
    #deal with batches...
        
    #NOTE: these are item-level conversion methods, and should be handled more clearly
    def formatsavedata(self, data):
        #TODO: swapping to JSON methodology for hbase will vastly improve 
        #the happiness here.
        return {'{}:data'.format(self._colfam):
                cPickle.dumps(data, cPickle.HIGHEST_PROTOCOL)}
    def formatsavedict(self, data):
        return dict([('{}:{}'.format(self._colfam, key), 
                       cPickle.dumps(value, cPickle.HIGHEST_PROTOCOL)) for
                      key, value in data.iteritems()])
        
    def loaddataformat(self, data):
        return cPickle.loads(data['m:data'])
    def loaddictformat(self, data):  
        return dict([(key.split(':', 1)[1], cPickle.loads(value)) for 
                     key, value in data.items()])
    
        
class MilieuTable(Table):
    
    def _milieu_keyify(self, mname, key):
            if not isinstance(key, tuple):
                key = (key,)
            return ':'.join((mname, ':'.join([str(k) for k in key])))
        
    def loadone(self, key):
        raise NotImplementedError
    
    def iter_milieu_data(self, milieu):
        keys = milieu.keys()
        rowset = self.native_tbl.rows([self._milieu_keyify(milieu.name, key)
                                       for key in keys])
        for key, val in itertools.izip(keys, rowset):
            yield key, val[1]
            
    def savemany(self, values, *args, **kwargs):
        super(MilieuTable, self).savemany([(self._milieu_keyify(kwargs['name'], 
                                                                key), value) for 
                                           key, value in values], *args, **kwargs)
        
class CoreTable(Table):

    def loadone(self, key):
        raise NotImplementedError

    def iter_core_samples(self, core):
        #I'd like to do this without having to do 2 db queries but I don't know
        #that the internal memory for loading & sorting locally is a better idea.
        #Going with this way, but alert to all kinds of perf issues
        allval = self.native_tbl.row('%s:all' % core.name)
        yield 'all', allval
        for key, value in self.native_tbl.scan(row_prefix=core.name):
            key = key.split(':', 1)[1]
            if key == 'all':
                #already got that one
                pass
            else:
                yield float(key), value
            
    def savemany(self, values, *args, **kwargs):
        def keyify(key):
            if key == 'all':
                return '{}:all'.format(kwargs['name'])
            else:
                return '{}:{:015f}'.format(kwargs['name'], key)
        super(CoreTable, self).savemany([(keyify(key), value) for 
                                         key, value in values],
                                        *args, **kwargs)
        
class MapTable(Table):
    
    def __init__(self, connection, myname, itemtablename):
        super(MapTable, self).__init__(connection, myname)
        self.itemtablename = itemtablename
        
    def do_create(self):
        super(MapTable, self).do_create()
        self.connection.create_table(self.itemtablename, 
                                     {self._colfam:{'max_versions':1}})
    
    def loadkeys(self):
        def backcompat(value):
            try:
                return cPickle.loads(value)
            except (cPickle.UnpicklingError, ValueError):
                #things starting with "int" try to unpickle as integers...
                return str(value)
        scanner = self.native_tbl.scan()
        try:
            result = {}
            #generators don't work in list comps, because argh.
            for key, v in scanner:
                result[key] = {}
                for k, value in v.iteritems():
                    result[key][k.split(':', 1)[1]] = backcompat(value)
            return result
        except happybase.hbase.ttypes.IllegalArgument:
            raise NameError
        
    
