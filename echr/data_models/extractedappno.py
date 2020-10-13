import peewee as pw
from echr.data_models.base import BaseModel
from echr.data_models.case import Case


class ExtractedApp(BaseModel):
    name = pw.CharField()
    isechr = pw.BooleanField(default=False)
    case = pw.ForeignKeyField(Case, backref='extractedapps')
