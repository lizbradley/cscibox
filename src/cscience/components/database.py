import happybase

class Database:
    
    def __init__(self):
        self.connection = happybase.Connection('localhost')
        current_tables = connection.tables()
        if 'calvin' not in current_tables:
            connection.create_table('calvin', 'cf':dict())
        self.table = connection.table('calvin')