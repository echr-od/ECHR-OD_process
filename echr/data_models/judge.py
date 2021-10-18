import peewee as pw
from echr.data_models.base import BaseModel


class Judge(BaseModel):
    name = pw.CharField(primary_key=True)
    full_name = pw.CharField()
    start = pw.IntegerField()
    end = pw.IntegerField(null=True)
