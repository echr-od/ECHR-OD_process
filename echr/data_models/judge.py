import peewee as pw
from echr.data_models.base import BaseModel
from playhouse.sqlite_ext import JSONField
from echr.data_models.case import Case


class Judge(BaseModel):
    name = pw.CharField(primary_key=True)
    full_name = pw.CharField()
    start = pw.IntegerField()
    end = pw.IntegerField(null=True)
