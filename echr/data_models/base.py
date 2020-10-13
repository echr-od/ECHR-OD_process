import peewee as pw

db = pw.SqliteDatabase(None)

class BaseModel(pw.Model):
    class Meta:
        database = db
