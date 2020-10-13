import peewee as pw
from echr.data_models.base import BaseModel


class Mention(BaseModel):
    id = pw.AutoField()
    mention = pw.CharField()
