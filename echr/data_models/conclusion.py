import peewee as pw
from echr.data_models.base import BaseModel
from echr.data_models.case import Case
from echr.data_models.detail import Detail
from echr.data_models.mention import Mention


class Conclusion(BaseModel):
    id = pw.AutoField()
    article = pw.CharField(null=True)
    base_article = pw.CharField(null=True)
    element = pw.CharField()
    type = pw.CharField()


class ConclusionDetail(BaseModel):
    detail = pw.ForeignKeyField(Detail, backref='in_ccl')
    conclusion = pw.ForeignKeyField(Conclusion, backref='details')


class ConclusionMention(BaseModel):
    mention = pw.ForeignKeyField(Mention, backref='in_ccl')
    conclusion = pw.ForeignKeyField(Conclusion, backref='mentions')


class ConclusionCase(BaseModel):
    conclusion = pw.ForeignKeyField(Conclusion, backref='in_cases')
    case = pw.ForeignKeyField(Case, backref='conclusions')

    class Meta:
        '''
            Metaclass to assign the primary key
        '''
        primary_key = pw.CompositeKey('conclusion', 'case')
