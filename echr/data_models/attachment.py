import peewee as pw
from playhouse.sqlite_ext import JSONField
from echr.data_models.base import BaseModel
from echr.data_models.case import Case


class Attachment(BaseModel):
    tag = pw.CharField(null=False)
    case = pw.ForeignKeyField(Case, backref='cases')

    class Meta:
        '''
            Metaclass to assign the primary key
        '''
        primary_key = pw.CompositeKey('tag', 'case')


class Table(Attachment):
    content = JSONField(null=False)

