import cPickle

import pymongo
import pymongo.son_manipulator

from quantities import Quantity
from cscience.framework.samples import UncertainQuantity

class Database(object):
    
    def __init__(self, data_source):
        self.connection = pymongo.MongoClient(data_source)['repository']
        self.connection.add_son_manipulator(HandleQtys())
        
    def table(self, tablename):
        return Table(self.connection, tablename)
    
    def ctable(self, tablename):
        return CoreTable(self.connection, tablename)
    
    def mtable(self, tablename):
        return MilieuTable(self.connection, tablename)
        
    def maptable(self, maptablename, itemtablename):
        return MapTable(self.connection, maptablename, itemtablename)
        
class Table(object):
    _keyfield = 'name'
    
    def __init__(self, connection, name):
        self.name = name
        self.connection = connection
        self.native_tbl = connection[name]
        
    def do_create(self):
        self.native_tbl.create_index(self._keyfield, unique=True)
        
    def loadone(self, key):
        return self.native_tbl.find_one({self._keyfield: key})
    def savemany(self, items, *args, **kwargs):
        batch = self.native_tbl.initialize_unordered_bulk_op()
        for key, value in items:
            #TODO: this might cause funny pointer issues. be alert.
            value[self._keyfield] = key
            batch.find({self._keyfield:key}).upsert().update({'$set':value})
        try:
            batch.execute()
        except:
            print items
            raise
        #currently no deletions are allowed, so this should work just fine.
        
    def loadkeys(self):
        cursor = self.native_tbl.find(fields=[self._keyfield])
        return [item[self._keyfield] for item in cursor]
        
    #NOTE: these are item-level conversion methods, and should be handled more clearly
    def formatsavedata(self, data):
        return {'pickled_data':unicode(cPickle.dumps(data, cPickle.HIGHEST_PROTOCOL))}
    def formatsavedict(self, data):
        return data
    def loaddataformat(self, data):
        return cPickle.loads(data['pickled_data'])
    def loaddictformat(self, data):  
        return data
    
        
class MilieuTable(Table):
            
    def loadone(self, key):
        raise NotImplementedError
    
    def iter_milieu_data(self, milieu):
        entries = self.native_tbl.find_one({self._keyfield:milieu.name},
                                           fields=['entries'])['entries']
        for item in entries:
            key = item['_saved_milieu_key']
            del item['_saved_milieu_key']
            yield key, item
            
    def savemany(self, items, *args, **kwargs):
        entries = []
        for key, value in items:
            if not isinstance(key, tuple):
                key = (key,)
            #TODO: this might cause funny pointer issues. be alert.
            value['_saved_milieu_key'] = key
            entries.append(value)
        self.native_tbl.update({self._keyfield:kwargs['name']},
                               {'$set':{'entries':entries}}, manipulate=True)
        
class CoreTable(Table):

    def loadone(self, key):
        raise NotImplementedError

    def iter_core_samples(self, core):
        entries = self.native_tbl.find_one({self._keyfield:core.name},
                                           fields=['entries'])['entries']
        for item in entries:
            key = float(item['_precise_sample_depth'])
            del item['_precise_sample_depth']
            yield key, item
            
    def savemany(self, values, *args, **kwargs):
        entries = []
        for key, value in items:
            #TODO: this might cause funny pointer issues. be alert.
            value['_precise_sample_depth'] = unicode(key)
            entries.append(value)
        self.native_tbl.update({self._keyfield:kwargs['name']},
                               {'$set':{'entries':entries}}, manipulate=True)
        
class MapTable(Table):
    
    def __init__(self, connection, myname, itemtablename):
        super(MapTable, self).__init__(connection, itemtablename)
        self.itemtablename = itemtablename
        
    def loadkeys(self):
        cursor = self.native_tbl.find(fields={'entries':False})
        return dict([(item[self._keyfield], item) for item in cursor])


class HandleQtys(pymongo.son_manipulator.SONManipulator):
    def handle_uncert_save(self, uncert):
        if uncert.distribution:
            return {'dist':cPickle.dumps(uncert.distribution, cPickle.HIGHEST_PROTOCOL)}
        else:
            if not uncert.magnitude:
                return {}
            return {'mag':[mag.magnitude for mag in uncert.magnitude]}
    def handle_uncert_load(self, value):
        if 'dist' in value:
            return cPickle.loads(value['dist'])
        elif value:
            if len(value['mag']) == 1:
                return value['mag'][0]
            else:
                return value['mag']
        else:
            return 0
    
    
    def transform_incoming(self, son, collection):
        for key, value in son.iteritems():
            if hasattr(value, 'units'):
                son[key] = {'_datatype':'quantity',
                            'magnitude':value.magnitude,
                            'units':unicode(value.units.dimensionality)}
                if hasattr(value, 'uncertainty'):
                    son[key]['uncertainty'] = self.handle_uncert_save(value.uncertainty)
            elif isinstance(value, dict):
                son[key] = self.transform_incoming(value, collection)
        return son

    def transform_outgoing(self, son, collection):
        for key, value in son.iteritems():
            if isinstance(value, dict):
                if value.get('_datatype', None) == 'quantity':
                    if 'uncertainty' in value:
                        son[key] = UncertainQuantity(value['magnitude'], value['units'],
                                                     self.handle_uncert_load(value['uncertainty']))
                    else:
                        son[key] = Quantity(value['magnitude'], value['units'])
                else:
                    son[key] = self.transform_outgoing(value, collection)
        return son
