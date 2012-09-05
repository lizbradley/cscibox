import os

class Template(object):

    def __init__(self):
        self.name   = None
        self.fields = {}
        self.order  = []
        self.key    = None

    def add_field(self, name, field_type):
        self.fields[name] = field_type
        if not name in self.order:
            self.order.append(name)

    def get_key(self):
        return self.key

    def get_field_type(self, name):
        return self.fields[name]

    def get_name(self):
        return self.name

    def get_order(self):
        return self.order[:]

    def has_field(self, name):
        return name in self.order

    def move_down(self, index):
        name = self.order.pop(index)
        self.order.insert(index+1,name)
        
    def move_up(self, index):
        name = self.order.pop(index)
        self.order.insert(index-1,name)

    def names(self):
        keys = self.fields.keys()
        keys.sort()
        return keys

    def remove_field(self, name):
        self.fields.pop(name)
        self.order.remove(name)
        if name == self.key:
            self.key = None
        
    def size(self):
        return len(self.order)

    def set_name(self, name):
        self.name = name

    def set_key(self, name):
        if name == None:
            self.key = None
        elif name in self.order:
            self.key = name
    
    def convert_field(self, field_type, value):
        if field_type == "string":
            value = str(value)
        elif field_type == "float":
            value = float(value)
        else:
            value = int(value)
        return value
        
    def newCollection(self, csv_file):
        """This method accepts a path to a .csv file and returns a dictionary that has the following structure:
               the template's key attribute is used to access the dictionary
               all remaining template attributes are stored in a dictionary referenced by the key attribute
            One exception to this rule is if the template contains only two attributes. In that case, the
            dictionary key directly accesses the value of the other attribute.
            csv_file must point to a csv file that contains one field per attribute defined in the template.
            If there is a problem with the .csv file, this method returns None.
            If the template has no key attribute, this method returns None.
            Finally, if the template has less than two fields, this method returns None."""
        key = self.get_key()
        if key == None:
            return None
        if self.size() < 2:
            return None
        collection = {}
        import csv
        input_file = file(csv_file, "U")
        r = csv.DictReader(input_file)
        for row in r:
            key_value = self.convert_field(self.get_field_type(key), row[key])
            other_fields = self.names()
            other_fields.remove(key)
            if len(other_fields) == 1:
                att = other_fields[0]
                field_value = self.convert_field(self.get_field_type(att), row[att])
                collection[key_value] = field_value
            else:
                entry = {}
                for att in other_fields:
                    field_value = self.convert_field(self.get_field_type(att), row[att])
                    entry[att] = field_value
                collection[key_value] = entry
        return collection

    def save(self, f):
        f.write(self.name)
        f.write(os.linesep)
        if self.key == None:
            f.write("")
        else:
            f.write(self.key)
        f.write(os.linesep)
        f.write(repr(self.fields))
        f.write(os.linesep)
        f.write(repr(self.order))
        f.write(os.linesep)

    def load(self, f):
        # read name
        self.name   = f.readline().strip()
        self.key    = f.readline().strip()
        if self.key == "":
            self.key = None
        self.fields = eval(f.readline().strip())
        self.order  = eval(f.readline().strip())
