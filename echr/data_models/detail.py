import peewee as pw
from echr.data_models.base import BaseModel


class Detail(BaseModel):
    id = pw.AutoField()
    detail = pw.CharField()
