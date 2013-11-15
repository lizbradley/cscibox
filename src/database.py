import happybase
import collections
import itertools
import cscience.datastore
from cscience.framework.samples import _types
from cscience.framework import Collection
import cscience.framework.paleobase

class DatabaseTemplateField(cscience.framework.paleobase.TemplateField):
    #TODO: add units?
    
    def __init__(self, name, field_type='float', iskey=False):
        self.name = name
        self.field_type = field_type
        self.iskey = iskey

class DatabaseTemplate(cscience.framework.paleobase.TemplateField.Template):
    #TODO: allow unkeyed milieus
    """
    A Template defines the format of a Milieu for loading from csv files/
    required attribute checking/etc.
    """

    def __init__(self, *args, **kwargs):
        self.name = kwargs.pop('name', '[NONE]')
        self.key_fields = []
        super(Template, self).__init__(*args, **kwargs)
        self.database = Database()
        
    def __iter__(self):
        for key in self.key_fields:
            yield key
        for key in self.iter_nonkeys():
            yield key
                
    def getitemat(self, index):
        return self.database.table(str(index))
    
    def iter_nonkeys(self):
        for key in super(Template, self).__iter__():
            if key not in self.key_fields:
                yield key

    def add_field(self, name, field_type, iskey=False):
        self[name] = TemplateField(name, field_type, iskey)

    def __setitem__(self, key, value):
        super(Template, self).__setitem__(key, value)
        if value.iskey:
            if key not in self.key_fields:
                self.key_fields.append(key)
        elif key in self.key_fields:
            self.key_fields.remove(value)
            
    def __delitem__(self, key, *args, **kwargs):
        super(Template, self).__delitem__(key, *args, **kwargs)
        try:
            self.key_fields.remove(key)
        except ValueError:
            pass
        
    def new_milieu(self, dictm):
        """This method accepts a dictionary and returns a Milieu
        loaded using this template from that dictionary:
         -the template's key attributes are used as a key in the Milieu
         -all remaining template attributes are stored as the values in the
         Milieu. See the Milieu documentation for further details.
        """
        
        if not self or len(self) < 2:
            #can't have a milieu with only one column (or no columns)
            raise ValueError()
        
        def convert_field(field, value):
            if value is None or value == '':
                return None
            tp = _types[field.field_type]
            try:
                return tp(value)
            except ValueError:
                #sometimes things we want to import as ints are expressed as
                #floats in the original source -- this fixes that issue
                return tp(float(value))
            
        if self.key_fields:
            def makekey(index, row):
                return tuple([convert_field(self[key], row[key]) 
                            for key in self.key_fields])
        else:
            def makekey(index, row):
                return (index,)
            
        milieu = Milieu(self)
        for index, row in enumerate(dictm):
            keyval = makekey(index, row)         
            try:
                milieu[keyval] = dict([(att, convert_field(self[att], row[att])) 
                                       for att in self.iter_nonkeys()])   
            except:
                print row, keyval
                for att in self.iter_nonkeys():
                    print self[att], row[att]
                raise
            
        return milieu
        
class Templates(Collection):
    _filename = 'templates'

class Milieu(dict):
    
    def __init__(self, template, name='[NONE]'):
        self.name = name
        self._template = template.name
        
    @property
    def template(self):
        return cscience.datastore.templates[self._template]
    
    def itervalues(self):
        for key, val in self.iteritems():
            val.update(dict(itertools.izip(self.template.key_fields, key)))
            yield val  
    
    def __getitem__(self, key):
        #TODO: make it so if it's a dictionary with one item, we return the 
        # value of the item instead of just the dict? 
        
        #get an item out of the collection. If the key passed is not a tuple
        #(and therefore not in the Milieu's keys), it will be automatically
        #tried as a tuple instead.
        try:
            return super(Milieu, self).__getitem__(key)
        except KeyError:
            return super(Milieu, self).__getitem__((key,))


class Milieus(Collection):
    _filename = 'milieus'

class Database:
    
    def __init__(self):
        self.connection = happybase.Connection('localhost')
        current_tables = self.connection.tables()
        if 'calvin' not in current_tables:
            self.connection.create_table('calvin', cf=dict())
        self.table = self.connection.table('calvin')


if __name__ == '__main__':
    database = Database
    print database.connection.tables()
    database.connection.close()
    row = database.table.row(str(102971380019192093573))
    print row
    for key,data in table.scan(filter = "SingleColumnValueFilter('c14','calib.14C  ' , =, 'substring:10297.0', true, false)"):
        print key,data