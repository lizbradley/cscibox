import bisect
import time
import cscience.datastore

from cscience.framework import Collection

def conv_bool(x):
    if not x:
        return None
    elif x[0].lower() in 'pyst1':
        return True
    else:
        return False

_types = {'string':unicode, 'boolean':conv_bool, 'float':float, 'integer':int}
        

class Attribute(object):

    def __init__(self, name, type_='string', unit='', output=False, has_error=False):
        self.name = name
        self.type_ = type_.lower()
        self.unit = unit
        self.output = output
        self.has_error = has_error

    def is_numeric(self):
        #TODO: this is a copy of a method in datastructures...
        return self.type_ in ('float', 'integer')

    @property
    def in_use(self):
        """
        Determine if an attribute is in use.
        Type of usage or blank string is returned
        """
        return 'All attributes now considered in use for sanity'
    
    @property
    def is_virtual(self):
        return False

    def input_value(self, value):
        """
        Takes a string and converts it to a Python-friendly value with
        type appropriate to the attribute (if known) or a string otherwise
        """
        try:
            return _types[self.type_](value)
        except KeyError:
            #means attribute not present, but honestly, SO?
            return unicode(value)
        #ValueError also possible; that should be re-raised

    def display_value(self, value):
        """
        Formats a Python attribute value for user visibility. Specifically:
        None -> 'N/A'
        numbers are nicely formatted
        strings that look like numbers are surrounded by quotes
        """
        if value is None:
            return 'N/A'
        try:
            return value.user_display()
        except AttributeError:
            return unicode(value)
        
    def LiPD_value(self, value):
        try:
            return value.LiPD_tuple()
        except AttributeError:
            return self.name, unicode(value)

class VirtualAttribute(Attribute):
    """
    A Virtual Attribute is a conceptual object that shows (hierarchically) one
    of some set of attributes from a sample. Conceptually, when a sample is
    asked for its value for an Attribute that is virtual, the value returned
    will be the value of the first non-null attribute in said sample from the
    list of combined attributes within the virtual attribute.

    (this is set up to work only on virtual samples, but since that's what
    you'll have in basically any case here anyway, that's not to be worried
    about)
    """
    def __init__(self, name, type_='string', aggatts=[]):
        self.name = name
        self.type_ = type_.lower()
        self.aggatts = aggatts


    def is_numeric(self):
        dst = cscience.datastore.Datastore()
        return all([dst.sample_attributes[att].is_numeric() for att in self.aggatts])
    
    @property
    def unit(self):
        dst = cscience.datastore.Datastore()
        return dst.sample_attributes[self.aggatts[0]].unit

    @property
    def is_virtual(self):
        return True

    def compose_value(self, sample):
        for att in self.aggatts:
            if sample[att] is not None:
                return sample[att]
        return None


base_atts = ['depth', 'run']
def basesorter(a, b):
    if a not in base_atts and b not in base_atts:
        return cmp(a, b)
    if a in base_atts:
        if b in base_atts:
            return cmp(base_atts.index(a), base_atts.index(b))
        return -1
    return 1
class Attributes(Collection):
    _tablename = 'atts'

    def __new__(self, *args, **kwargs):
        instance = super(Attributes, self).__new__(self, *args, **kwargs)
        instance.sorted_keys = base_atts[:]
        instance.base_atts = base_atts
        return instance
    def __init__(self, *args, **kwargs):
        super(Attributes, self).__init__(*args, **kwargs)
        self.sorted_keys = sorted(self.keys(), cmp=basesorter)

    def __iter__(self):
        for key in self.sorted_keys:
            yield self[key]
    def __setitem__(self, index, item):
        if index not in self.sorted_keys:
            #Keys (currently run, depth) stay out of sorting.
            bisect.insort(self.sorted_keys, index, len(base_atts))
        return super(Attributes, self).__setitem__(index, item)

    def byindex(self, index):
        return self[self.getkeyat(index)]
    def getkeyat(self, index):
        return self.sorted_keys[index]
    def indexof(self, key):
        return self.sorted_keys.index(key)

    def input_value(self, att, value):
        """
        Takes a string and converts it to a Python-friendly value with
        type appropriate to the attribute (if known) or a string otherwise
        """
        return self[att].input_value(value)

    def get_unit(self, att):
        return self[att].unit
    def add_attribute(self, name, type, unit, isoutput, haserror):
        self[name] = Attribute(name, type, unit, isoutput, haserror)
    def add_virtual_att(self, name, aggregate):
        if aggregate:
            type_ = aggregate[0].type_
        else:
            type_ = 'string'
        #no unit
        self[name] = VirtualAttribute(name, type_, [agg.name for agg in aggregate])

    def virtual_atts(self):
        return sorted([att.name for att in self if att.is_virtual])

    def display_value(self, att, value):
        """
        Formats a Python attribute value for user visibility. Specifically:
        None -> 'N/A'
        numbers are nicely formatted
        strings that look like numbers are surrounded by quotes
        """
        return self[att].display_value(value)

    @classmethod
    def bootstrap(cls, connection):
        instance = super(Attributes, cls).bootstrap(connection)
        instance.sorted_keys = base_atts[:]
        instance['depth'] = Attribute('depth', 'float', 'centimeters')
        instance['run'] = Attribute('run')
        return instance
    
class CoreAttributes(Collection):
    _tablename = 'coreatts'

    def add_attribute(self, name, type, unit, isoutput, haserror):
        self[name] = Attribute(name, type, unit, isoutput, haserror)
    def __iter__(self):
        for key in self.keys():
            yield self[key]

    @classmethod
    def bootstrap(cls, connection):
        instance = super(CoreAttributes, cls).bootstrap(connection)
        instance['Provenance'] = Attribute('Provenance')
        instance['Age/Depth Model'] = Attribute('Age/Depth Model', 'age model', '', True)
        instance['Calculated On'] = Attribute('Calculated On', 'time')
        instance['Required Citations'] = Attribute('Required Citations', 'publication list')
        instance['Core Site'] = Attribute('Core Site', 'geography')
        instance['Core GUID'] = Attribute('Core GUID')
        return instance
    