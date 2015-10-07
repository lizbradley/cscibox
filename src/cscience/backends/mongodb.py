import cPickle
import json
import time
import sys

import pymongo
import pymongo.son_manipulator

import scipy.interpolate
from quantities import Quantity
from cscience.framework.samples import UncertainQuantity
from cscience.components import c_calibration

class Database(object):

    def __init__(self, data_source, port):
        self.connection = pymongo.MongoClient(data_source, port)['repository']
        self.connection.add_son_manipulator(CustomTransformations())

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
        if not items:
            return
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
        return {'pickled_data':unicode(cPickle.dumps(data))}
    def formatsavedict(self, data):
        return data
    def loaddataformat(self, data):
        return cPickle.loads(str(data['pickled_data']))
    def loaddictformat(self, data):
        return data


class MilieuTable(Table):

    def loadone(self, key):
        raise NotImplementedError

    def iter_milieu_data(self, milieu):
        entries = self.native_tbl.find_one({self._keyfield:milieu.name},
                                           fields=['entries'])['entries']
        for item in entries:
            key = tuple(item['_saved_milieu_key'])
            del item['_saved_milieu_key']
            yield key, item

    def savemany(self, items, *args, **kwargs):
        if not items:
            return
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
                                           fields=['entries']).get('entries', [])
        #need to make sure all is first! (this does so hackily)
        entries.sort(key=lambda item: item['_precise_sample_depth'], reverse=True)
        
        for item in entries:
            if item['_precise_sample_depth'] == 'all':
                key = 'all'
            else:
                key = float(item['_precise_sample_depth'])
            del item['_precise_sample_depth']
            yield key, item

    def savemany(self, items, *args, **kwargs):
        if not items:
            return
        entries = []
        for key, value in items:
            #TODO: this might cause funny pointer issues. be alert.
            val = value.copy()
            val['_precise_sample_depth'] = unicode(key)
            entries.append(val)
        
        self.native_tbl.update({self._keyfield:kwargs['name']},
                        {'$set':{'entries':entries}}, manipulate=True)

class MapTable(Table):

    def __init__(self, connection, myname, itemtablename):
        super(MapTable, self).__init__(connection, itemtablename)
        self.itemtablename = itemtablename

    def loadkeys(self):
        cursor = self.native_tbl.find(fields={'entries':False})
        return dict([(item[self._keyfield], item) for item in cursor])

class InterpolatedFuncs(object):
    def transform_item_in(self, value):
        #TODO: this is gross and should be generalized, but I'm not totally
        #sure how yet, so I'm handling the one case I have for now.
        if value.__class__.__name__ == 'interp1d':
            return {'_datatype':'interp1d',
                   'kind':unicode(value._kind),
                   'x':list(value.x),
                   'y':list(value.y)}
        elif value.__class__.__name__ == 'InterpolatedUnivariateSpline':
            #grosssssssssssssssss; but this seems to be the best available way
            #to save-and-restore our friend the spline :P
            #(as I'm trying to avoid the whole pickle shizzle)
            return {'_datatype':'InterpolatedUnivariateSpline',
                    'x':list(value._data[0]),
                    'y':list(value._data[1]),
                    'k':int(value._eval_args[2])}
        return value

    def transform_dict_out(self, value):
        if value.get('_datatype', None) == 'interp1d':
            kind = value['kind']
            if kind == 'spline':
                kind = 'slinear'
            return scipy.interpolate.interp1d(value['x'], value['y'], kind=kind,
                                              bounds_error=False, fill_value=None)
        elif value.get('_datatype', None) == 'InterpolatedUnivariateSpline':
            try:
                return scipy.interpolate.InterpolatedUnivariateSpline(
                                    value['x'], value['y'], k=value['k'])
            except:
                print 'bypassed broken saved-spline...'
                return 'ERROR'
        return None

class HandleQtys(object):
    def handle_uncert_save(self, uncert):
        if uncert.distribution:
            return {'dist':unicode(cPickle.dumps(uncert.distribution))}
        else:
            if not uncert.magnitude:
                return {}
            return {'mag':[unicode(mag.magnitude) for mag in uncert.magnitude]}
    def handle_uncert_load(self, value):
        if 'dist' in value:
            return cPickle.loads(str(value['dist']))
        elif value:
            if len(value['mag']) == 1:
                return float(value['mag'][0])
            else:
                return [float(val) for val in value['mag']]
        else:
            return 0

    def transform_item_in(self, value):
        if hasattr(value, 'units'):
            val = {'_datatype':'quantity',
                   'magnitude':unicode(value.magnitude),
                   'units':unicode(value.units.dimensionality)}
            if hasattr(value, 'uncertainty'):
                val['uncertainty'] = self.handle_uncert_save(value.uncertainty)
            return val
        return value

    def transform_dict_out(self, value):
        if value.get('_datatype', None) == 'quantity':
            if 'uncertainty' in value:
                return UncertainQuantity(value['magnitude'], value['units'],
                                             self.handle_uncert_load(value['uncertainty']))
            else:
                return Quantity(value['magnitude'], value['units'])
        return None
    
class TimeEncoder(object):
    def transform_item_in(self, value):
        if isinstance(value, time.struct_time):
            return {'timeval':list(value)}
        return value
    def transform_dict_out(self, value):
        if 'timeval' in value:
            return time.struct_time(value['timeval'])
        return None

class CustomTransformations(pymongo.son_manipulator.SONManipulator):

    def __init__(self):

        self.transformers = [HandleQtys(), InterpolatedFuncs(), TimeEncoder()]

    def do_item_incoming(self, value):
        for trans in self.transformers:
            value = trans.transform_item_in(value)
        return value

    def transform_incoming_item(self, value, collection):
        if isinstance(value, dict):
            return self.transform_incoming(value, collection)
        elif isinstance(value, list) or isinstance(value, tuple):
            return [self.transform_incoming_item(item, collection) for item in value]
        else:
            return self.do_item_incoming(value)

    def transform_incoming(self, son, collection):
        son = son.copy()
        for key, value in son.iteritems():
            son[key] = self.transform_incoming_item(value, collection)
        return son

    def do_item_outgoing(self, value, collection):
        for trans in self.transformers:
            val = trans.transform_dict_out(value)
            if val:
                return val
        return self.transform_outgoing(value, collection)

    def transform_outgoing_item(self, value, collection):
        if isinstance(value, dict):
            return self.do_item_outgoing(value, collection)
        elif isinstance(value, list):
            return [self.transform_outgoing_item(item, collection) for item in value]
        else:
            return value

    def transform_outgoing(self, son, collection):
        for key, value in son.iteritems():
            son[key] = self.transform_outgoing_item(value, collection)
        return son
