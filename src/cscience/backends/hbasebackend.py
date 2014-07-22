import happybase
import cPickle

class Database(object):
    
    def __init__(self, data_source):
        self.connection = happybase.Connection(source)
        
    def table(self, tablename):
        return Table(self.connection, tablename)
        
    def maptable(self, maptablename, itemtablename):
        return MapTable(self.connection, maptablename, itemtablename)
    
    @staticmethod
    def _milieu_keyify(mname, key):
            if not isinstance(key, tuple):
                key = (key,)
            return ':'.join((mname, ':'.join([str(k) for k in key])))
        
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
    def loadmany(self, keys):
        return self.native_tbl.rows(keys)
    def savemany(self, items):
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
        """
        data is either a dictionary of values to be saved or a single object. 
        Returned is a "value" the database backend will be happy with.
        """
        #TODO: swapping to JSON methodology for hbase will vastly improve 
        #the happiness here.
        return {'{}:data'.format(self._colfam):
                cPickle.dumps(data, cPickle.HIGHEST_PROTOCOL)}
    def formatsavedict(self, data):
        return dict(*[('{}:{}'.format(self._colfam, key), 
                       cPickle.dumps(value, cPickle.HIGHEST_PROTOCOL)) for
                      key, value in data.iteritems()])
        
    def loaddataformat(self, data):
        return cPickle.loads(data['m:data'])
    def loaddictformat(self, data):
        def backcompat(value):
            try:
                return cPickle.loads(value)
            except UnpicklingError:
                return str(value)
        return dict([(key.split(':', 1)[1], backcompat(value)) 
                     for key, value in data.iteritems()])
        
        
    #this is kind of design-gross, but I'm not sure how better to deal with it
    #right this instant
    def iter_core_samples(self, core):
        for key, value in self.native_tbl.scan(row_prefix=core.name):
            yield float(key.split(':', 1)[1]), value
    def save_whole_core(self, cname, values):
        def keyify(key):
            return '{}:{:015f}'.format(cname, key)
        self.savemany([(keyify(key), value) for key, value in values])
    
    def iter_milieu_data(self, milieu):
        keys = milieu.keys()
        rowset = self.native_tbl.rows([Database._milieu_keyify(milieu.name, key)
                                       for key in keys])
        for key, val in itertools.izip(keys, rowset):
            yield key, val[1]
    def save_whole_milieu(self, mname, values):
        self.savemany([(Database._milieu_keyify(mname, key), value) for 
                       key, value in values])
    
    
        
class MapTable(Table):
    
    def __init__(self, connection, myname, itemtablename):
        super(MapTable, self).__init__(connection, myname)
        self.itemtablename = itemtablename
        
    def do_create(self):
        super(MapTable, self).do_create()
        self.connection.create_table(self.itemtablename, 
                                     {self._colfam:{'max_versions':1}})
    
    def loadkeys(self):
        scanner = self.native_tbl.scan()
        try:
            return self.loaddictformat(scanner)
        except happybase.hbase.ttypes.IllegalArgument:
            raise NameError
        
    