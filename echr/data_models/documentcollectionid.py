import peewee as pw
from echr.data_models.base import BaseModel
from echr.data_models.case import Case


class DocumentCollectionId(BaseModel):
    name = pw.CharField()
    case = pw.ForeignKeyField(Case, backref='documentcollectionids')
