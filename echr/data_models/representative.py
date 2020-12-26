import peewee as pw
from echr.data_models.base import BaseModel
from echr.data_models.case import Case


class Representative(BaseModel):
    name = pw.CharField()


class RepresentativeCase(BaseModel):
    representative = pw.ForeignKeyField(Representative, backref='representsin')
    case = pw.ForeignKeyField(Case, backref='representedby')

    class Meta:
        '''
            Metaclass to assign the primary key
        '''
        primary_key = pw.CompositeKey('representative', 'case')
