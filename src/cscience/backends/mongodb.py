import cPickle
import json
import time
import sys
import traceback
import logging

import pymongo
import gridfs
import pymongo.son_manipulator
from pymongo.collection import Collection

import scipy.interpolate
from quantities import Quantity
from cscience.framework import datastructures

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
        value = self.native_tbl.find_one({self._keyfield: key})
        return CustomTransformations().transform_outgoing_item(value, None)
    def savemany(self, items, *args, **kwargs):
        if not items:
            return
        batch = self.native_tbl.initialize_unordered_bulk_op()
        for key, value in items:
            #TODO: this might cause funny pointer issues. be alert.
            value[self._keyfield] = key
            #this is a little bit hackish but it lets me trivially apply the
            #same manipulations for son-ifying whether things are being stored
            #as a file or an actual document.
            value = CustomTransformations().transform_incoming_item(value, None)
            batch.find({self._keyfield:key}).upsert().update({'$set':value})
        try:
            batch.execute()
        except:
            print items
            raise

    # query is a dict filter.  Will delete the 1st that matches.
    def delete_one(self, query):
        self.native_tbl.remove(spec_or_id=query, multi=False)

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

class LargeTable(Table):

    def __init__(self, connection, name):
        self.name = name
        self.connection = connection
        self.fs = gridfs.GridFS(self.connection, collection=self._filetype)

    def do_create(self):
        self.fs._GridFS__files.ensure_index('name', unique=True)

    def loadone(self, key):
        raise NotImplementedError

    def savemany(self, items, *args, **kwargs):
        if not items:
            return
        entries = []
        for key, value in items:
            val = value.copy()
            val = self.keytransform(key, val)
            entries.append(val)

        #TODO: can use the auto-versioning inherent in gridfs's functionality
        #to save older versions of a core, if we want...
        try:
            oldversion = self.fs.get_last_version(**{self._keyfield:kwargs['name']})
        except gridfs.NoFile:
            pass
        else:
            self.fs.delete(oldversion._id)

        try:
            newfile = self.fs.new_file(**{self._keyfield:kwargs['name']})

            #this is a little bit hackish but it lets me trivially apply the
            #same manipulations for son-ifying whether things are being stored
            #as a file or an actual document.
            entries = CustomTransformations().transform_incoming_item(entries, None)
            json.dump(entries, newfile)
        except:
            print sys.exc_info()
            print traceback.format_exc()
        finally:
            newfile.close()

    def _load_many(self, value):
        try:
            myfile = self.fs.get_last_version(**{self._keyfield:value.name})
        except gridfs.NoFile:
            return []

        try:
            data = json.load(myfile)
            #same as encoding hack above
            data = CustomTransformations().transform_outgoing_item(data, None)
            return data
        finally:
            myfile.close()

        return []


class MilieuTable(LargeTable):
    _filetype = 'milieu_files'

    def keytransform(self, key, value):
        if not isinstance(key, tuple):
                key = (key,)

        value['_saved_milieu_key'] = key
        return value

    def iter_milieu_data(self, milieu):
        entries = self._load_many(milieu)

        for item in entries:
            key = tuple(item['_saved_milieu_key'])
            del item['_saved_milieu_key']
            yield key, item

class CoreTable(LargeTable):
    _filetype = 'core_files'

    def delete_item(self, key):
        try:
            oldversion = self.fs.get_last_version(**{self._keyfield:key})
        except gridfs.NoFile:
            pass
        else:
            self.fs.delete(oldversion._id)

    def keytransform(self, key, value):
        value['_precise_sample_depth'] = unicode(key)
        return value

    def iter_core_samples(self, core):
        entries = self._load_many(core)

        #need to make sure all is first! (this does so hackily)
        entries.sort(key=lambda item: item['_precise_sample_depth'], reverse=True)

        for item in entries:
            if item['_precise_sample_depth'] == 'all':
                #this stays to allow loading of cores that got saved pre-properties switchover
                key = 'all'
            else:
                key = float(item['_precise_sample_depth'])
            del item['_precise_sample_depth']
            yield key, item

class MapTable(Table):
    #TODO: sure would be nice to actually save the _ids instead of having to
    #re-fetch them for reading & writing elsewhere...

    def __init__(self, connection, myname, itemtablename):
        super(MapTable, self).__init__(connection, itemtablename)
        self.itemtablename = itemtablename

    def loadkeys(self):
        cursor = self.native_tbl.find()
        return dict([(item[self._keyfield], item) for item in cursor])

    def delete_item(self, key):
        self.native_tbl.remove({self._keyfield:key})


class PointLists(object):
    def transform_item_in(self, value):
        #TODO: capture other types of stored funcs (eg bacon fuzz)
        if hasattr(value, 'csv_data'):
            return {'_datatype' : 'baconinfo',
                    'csv_data' : value.csv_data,
                    'run_str' : value.run_str}

        if hasattr(value, 'xpoints') and hasattr(value, 'ypoints'):
            return {'_datatype':'pointlist',
                    'xpoints' : list(value.xpoints),
                    'ypoints' : list(value.ypoints),
                    'run_str' : value.run_str}
        return value

    def transform_dict_out(self, value):
        if value.get('_datatype', None) == 'baconinfo':
            return datastructures.BaconInfo(value['csv_data'], value['run_str'])

        if value.get('_datatype', None) == 'pointlist':
            return datastructures.PointlistInterpolation(value['xpoints'], value['ypoints'],
                    value['run_str'])
        return None


class HandleQtys(object):
    def handle_uncert_save(self, uncert):
        if uncert.distribution:
            return {'dist':{'x':list(uncert.distribution.x),
                            'y':list(uncert.distribution.y),
                            'avg':uncert.distribution.average,
                            'rng':uncert.distribution.range}}
        else:
            if not uncert.magnitude:
                return {}
            return {'mag':[unicode(mag.magnitude) for mag in uncert.magnitude]}
    def handle_uncert_load(self, value):
        if 'dist' in value:
            try:
                return datastructures.ProbabilityDistribution(
                            value['dist']['x'], value['dist']['y'],
                            value['dist']['avg'], value['dist']['rng'], False)
            except TypeError:
                return None
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
                return datastructures.UncertainQuantity(value['magnitude'], value['units'],
                                             self.handle_uncert_load(value['uncertainty']))
            else:
                return Quantity(value['magnitude'], value['units'])
        return None

class ConversionEncoder(object):
    def transform_item_in(self, value):
        if isinstance(value, time.struct_time):
            print 'still running into outgoing times...'
            return {'timeval':list(value)}
        return value
    def transform_dict_out(self, value):
        '''
        Returns the modified dict or None if no change needed
        '''
        if 'Latitude' in value and 'Longitude' in value:
            # if we have "Latitude" and "Longitude" properties
            # replace them with a GeographyData object
            val = value.copy()
            lat = val.pop('Latitude')
            lon = val.pop('Longitude')
            elev = val.pop('Elevation', None)
            val['Core Site'] = datastructures.GeographyData(lat, lon, elev)
            return val
        if 'timeval' in value:
            #Switch to using new, awesome times!
            return datastructures.TimeData(time.struct_time(value['timeval']))
        return None

class LiPDObjEncoder(object):
    #It's important that this guy go last, since *some* data types that we know
    #how to send to LiPD have different mongodb formats, and are handled by
    #other parsers.
    def transform_item_in(self, value):
        if hasattr(value, 'LiPD_tuple'):
            return dict([value.LiPD_tuple()])
        return value
    def transform_dict_out(self, value):
        #TODO: build a slightly better switch for this
        if 'geo' in value:
            return datastructures.GeographyData.parse_value(value['geo'])
        elif 'timestamp' in value:
            return datastructures.TimeData.parse_value(value['timestamp'])
        elif 'time' in value:
            return datastructures.TimeData.parse_value(value['time'])
        elif 'publist' in value:
            return datastructures.PublicationList.parse_value(value['publist'])
        elif 'pub' in value:
            return datastructures.PublicationList.parse_value(value['pub'])
        return None

class CustomTransformations(pymongo.son_manipulator.SONManipulator):

    def __init__(self):
        self.transformers = [HandleQtys(), PointLists(), ConversionEncoder(), LiPDObjEncoder()]

    def will_copy(self):
        return True

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
            if val is not None:
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
