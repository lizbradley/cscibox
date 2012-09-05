import os
import os.path

class Collections(object):

    def __init__(self):
        self.collections = {}

    def __str__(self):
        return '%s' % (self.collections)

    __repr__ = __str__

    def add(self, name, template, collection):
        self.collections[name] = [template,collection]
        
    def contains(self, name):
        return name in self.collections.keys()

    def remove(self, name):
        del(self.collections[name])

    def get(self, name):
        return self.collections[name][1]

    def get_template(self, name):
        return self.collections[name][0]

    def names(self):
        keys = self.collections.keys()
        keys.sort()
        return keys

    def save(self, path):
        collections_path =  os.path.join(path, 'collections')

        if not os.path.exists(collections_path):
            os.mkdir(collections_path)

        collection_names = self.names()

        # delete collections no longer in self.collections
        items = os.listdir(collections_path)
        to_delete = [old_file for old_file in items if not old_file[0:len(old_file)-4] in items]
        for old_file in to_delete:
            file_path = os.path.join(collections_path, old_file)
            os.remove(file_path)

        for name in collection_names:
            collection = self.get(name)
            template   = self.get_template(name)
            output_file = file(os.path.join(collections_path,name + ".txt"), "w")
            output_file.write(template)
            output_file.write(os.linesep)
            output_file.write(repr(collection))
            output_file.write(os.linesep)
            output_file.flush()
            output_file.close()

    def load(self, path):
        collections_path =  os.path.join(path, 'collections')

        if not os.path.exists(collections_path):
            os.mkdir(collections_path)

        items = os.listdir(collections_path)
        files = [item for item in items if item.endswith('.txt')]
        for input_file in files:
            f = open(os.path.join(collections_path,input_file), "U")
            template = f.readline().strip()
            data = f.read()
            f.close()
            collection = eval(data)
            self.add(input_file[0:len(input_file)-4], template, collection)