import peewee as pw
from playhouse.sqlite_ext import JSONField
from echr.data_models.base import BaseModel


class Case(BaseModel):
    itemid = pw.CharField(primary_key=True)

    docname = pw.CharField()
    doctypebranch = pw.CharField()
    ecli = pw.CharField(unique=True)
    importance = pw.IntegerField()
    applicability = pw.CharField()
    appno = pw.CharField()

    decisiondate = pw.DateTimeField(null=True)
    introductiondate = pw.DateTimeField(null=True)
    judgementdate = pw.DateTimeField(null=True)
    kpdate = pw.DateTimeField(null=True)
    languageisocode = pw.CharField()
    originatingbody_name = pw.CharField()
    originatingbody_type = pw.CharField()
    rank = pw.CharField()
    respondent = pw.CharField()
    separateopinion = pw.BooleanField()
    typedescription = pw.IntegerField()

    judgment = JSONField(null=True)
