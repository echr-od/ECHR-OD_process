import peewee as pw
from echr.data_models.base import BaseModel
from echr.data_models.case import Case


class DecisionBodyMember(BaseModel):
    id = pw.AutoField()
    name = pw.CharField()
    role = pw.CharField(null=True)


class DecisionBodyCase(BaseModel):
    member = pw.ForeignKeyField(DecisionBodyMember)
    case = pw.ForeignKeyField(Case, backref='decisionbody')

    class Meta:
        '''
            Metaclass to assign the primary key
        '''
        primary_key = pw.CompositeKey('member', 'case')
