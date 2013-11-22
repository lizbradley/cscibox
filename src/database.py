import happybase
import collections
import itertools
import cscience.datastore
from cscience.framework.samples import _types
from cscience.framework import Collection
import cscience.framework.paleobase


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