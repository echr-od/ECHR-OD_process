import peewee as pw
from echr.data_models.base import BaseModel
from echr.data_models.case import Case


class Party(BaseModel):
    name = pw.CharField()


class PartyCase(BaseModel):
    party = pw.ForeignKeyField(Party, backref='cases')
    case = pw.ForeignKeyField(Case, backref='parties')

    class Meta:
        '''
            Metaclass to assign the primary key
        '''
        primary_key = pw.CompositeKey('party', 'case')
