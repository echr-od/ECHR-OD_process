import peewee as pw

db = pw.SqliteDatabase(None)

class BaseModel(pw.Model):
    class Meta:
        '''
            Metaclass to assign the actual database
        '''
        database = db
