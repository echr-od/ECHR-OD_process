import peewee as pw
from echr.data_models.base import BaseModel
from echr.data_models.case import Case


class SCL(BaseModel):
    name = pw.CharField()


class SCLCase(BaseModel):
    scl = pw.ForeignKeyField(SCL, backref='citedin')
    case = pw.ForeignKeyField(Case, backref='scl')

    class Meta:
        '''
            Metaclass to assign the primary key
        '''
        primary_key = pw.CompositeKey('scl', 'case')
