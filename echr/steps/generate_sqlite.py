from playhouse.shortcuts import dict_to_model
from datetime import datetime
import argparse
import json
import os
from os import listdir
from os.path import isfile
from echr.utils.logger import getlogger
from echr.utils.cli import TAB
from rich.markdown import Markdown
from rich.console import Console
from rich.progress import (
    Progress,
    BarColumn,
    TimeRemainingColumn,
)

log = getlogger()

__console = Console(record=True)

from echr.data_models.base import db
from echr.data_models.case import Case
from echr.data_models.article import Article
from echr.data_models.attachment import Table, Attachment
from echr.data_models.conclusion import Conclusion, ConclusionCase, ConclusionDetail, ConclusionMention
from echr.data_models.detail import Detail
from echr.data_models.mention import Mention
from echr.data_models.party import Party, PartyCase
from echr.data_models.kpthesaurus import KPThesaurus
from echr.data_models.representative import Representative, RepresentativeCase
from echr.data_models.issue import Issue
from echr.data_models.documentcollectionid import DocumentCollectionId
from echr.data_models.extractedappno import ExtractedApp
from echr.data_models.scl import SCL, SCLCase
from echr.data_models.decisionbody import DecisionBodyMember, DecisionBodyCase
from echr.data_models.externalsource import ExternalSource


def create_tables():
    with db:
        db.create_tables([Case, Article, Conclusion, ConclusionCase, DecisionBodyMember, DecisionBodyCase,
                          ConclusionDetail, Detail, ConclusionMention,
                          Mention, Party, PartyCase, Representative, RepresentativeCase, KPThesaurus, ExternalSource,
                          Issue, DocumentCollectionId, ExtractedApp, SCL, SCLCase, Attachment, Table])

def populate_database(console, build, update):
    input_folder = os.path.join(build, 'raw', 'preprocessed_documents')
    cases_files = [os.path.join(input_folder, f) for f in listdir(input_folder)
                   if isfile(os.path.join(input_folder, f)) and '.json' in f]

    db.connect()
    if True:
        with Progress(
                TAB + "> Adding cases... [IN PROGRESS]\n",
                BarColumn(30),
                TimeRemainingColumn(),
                "| Adding case [blue]{task.fields[doc]} [white]({task.completed}/{task.total})"
                "{task.fields[error]}",
                transient=True,
                console=console
        ) as progress:
            task = progress.add_task("Adding...", total=len(cases_files), error="", doc=cases_files[0].split('/')[-1])
            for f in cases_files:
                with open(f, 'r') as f:
                    case = json.load(f)
                entity = Case.get_or_none(Case.itemid == case['itemid'])
                error = ""
                if entity is None:
                    try:
                        with db.atomic():
                            date_keys = ['decisiondate', 'introductiondate', 'judgementdate', 'kpdate']
                            for k in date_keys:
                                if case[k]:
                                    try:
                                        case[k] = datetime.strptime(case[k], '%d/%m/%Y %H:%M:%S')
                                    except:
                                        case[k] = datetime.strptime(case[k], '%d/%m/%Y')
                                else:
                                    del case[k]
                            parties = case.get('parties', [])
                            if 'parties' in case:
                                del case['parties']
                            decisionbody = case.get('decision_body', [])
                            if 'decision_body' in case:
                                del case['decision_body']
                            representedby = case.get('representedby', [])
                            if 'representedby' in case:
                                del case['representedby']
                            kpthesaurus = case.get('kpthesaurus', [])
                            if 'kpthesaurus' in case:
                                del case['kpthesaurus']
                            issues = case.get('issue', [])
                            if 'issue' in case:
                                del case['issue']
                            documentcollectionid = case.get('documentcollectionid', [])
                            if 'documentcollectionid' in case:
                                del case['documentcollectionid']
                            extractedappno = case.get('extractedappno', [])
                            if 'extractedappno' in case:
                                del case['extractedappno']
                            externalsources = case.get('externalsources', [])
                            if 'externalsources' in case:
                                del case['externalsources']
                            scls = case.get('scl', [])
                            if 'scl' in case:
                                del case['scl']
                            case['judgment'] = case['content']['{}.docx'.format(case['itemid'])]
                            del case['originatingbody']

                            attachments = case.get('attachments', {})
                            if 'attachments' in case:
                                del case['attachments']

                            i = dict_to_model(Case, case, ignore_unknown=True)
                            i.save(force_insert=True)

                            for doc, att in attachments.items():
                                for tag, content in att.items():
                                    if tag.startswith('table'):
                                        Table.get_or_create(tag=tag, case=i, content=content)

                            for scl in scls:
                                r = SCL.get_or_create(name=scl.title())
                                SCLCase.get_or_create(scl=r[0], case=i)

                            for source in externalsources:
                                ExternalSource.get_or_create(name=source, case=i)

                            for appno in extractedappno:
                                ExtractedApp.get_or_create(name=appno, case=i)

                            for doc in documentcollectionid:
                                DocumentCollectionId.get_or_create(name=doc, case=i)

                            for issue in issues:
                                Issue.get_or_create(name=issue, case=i)

                            for kp in kpthesaurus:
                                KPThesaurus.get_or_create(name=kp, case=i)

                            for representative in representedby:
                                r = Representative.get_or_create(name=representative.title())
                                RepresentativeCase.get_or_create(representative=r[0], case=i)

                            for member in decisionbody:
                                bodymember = DecisionBodyMember.get_or_create(name=member['name'], role=member.get('role', '').title())
                                DecisionBodyCase.get_or_create(member=bodymember[0], case=i)

                            for party in parties:
                                p = Party.get_or_create(name=party)
                                PartyCase.get_or_create(party=p[0], case=i)

                            for article in case['article']:
                                Article.get_or_create(title=article, case=i)
                            for element in case['conclusion']:
                                details = element.get('details', [])
                                if 'details' in element:
                                    del element['details']
                                mentions = element.get('mentions', [])
                                if 'mentions' in element:
                                    del element['mentions']
                                c = Conclusion.get_or_create(**element)
                                ConclusionCase.get_or_create(conclusion=c[0], case=i)
                                for detail in details:
                                    d = Detail.get_or_create(detail=detail)
                                    ConclusionDetail.get_or_create(detail=d[0], conclusion=c[0])
                                for mention in mentions:
                                    m = Mention.get_or_create(mention=mention)
                                    ConclusionMention.get_or_create(mention=m[0], conclusion=c[0])
                    except Exception as e:
                        log.debug(e)
                        error = '\n| Failed to add case {}'.format(case['itemid'])
                        error += '\n| {}'.format(str(e))
                else:
                    error = "\n| Skip as case already exists in the database"
                progress.update(task, advance=1, error=error, doc=case['itemid'])
        print(TAB + "> Adding cases... [green][DONE]")

        '''
        with Progress(
                TAB + "> Adjusting cross-references... [IN PROGRESS]\n",
                BarColumn(30),
                TimeRemainingColumn(),
                "| Adjusting reference [white]({task.completed}/{task.total})"
                "{task.fields[error]}",
                transient=True,
        ) as progress:
            query = list(ExtractedApp.select())
            query = [e for e in query if not e.isechr]
            task = progress.add_task("Adjusting reference...", total=len(query), error="")
            for i, e in enumerate(query):
                error = ''
                try:
                    with db.atomic():
                        r = list(Case.select().where(Case.appno == e.name))
                        if r:
                            e.update(isechr=True)
                            e.save()
                except Exception as e:
                    log.debug(e)
                    error = '\n| Failed to add relation for {}'.format(e.name)
                    error += '\n| {}'.format(str(e))
                progress.update(task, advance=1, error=error)
        print(TAB + "> Adjusting cross-references... [green][DONE]")
        '''
    db.close()


def run(console, build, cases=None, force=True, update=True):
    __console = console
    global print
    print = __console.print

    print(Markdown("- **Step configuration**"))

    db_path = os.path.join(build, 'structured', 'echr-db.db')
    db_recreated = False
    if not update and os.path.isfile(db_path):
        if force:
            print(TAB + "> Removing database... [green][DONE]")
            os.remove(db_path)
            db_recreated = True
        else:
            exit(1)

    if not os.path.isfile(db_path):
        db_recreated = True

    print(Markdown("- **Generate SQL database**"))
    global db
    db.init(db_path, pragmas={'foreign_keys': 1})
    print(TAB + "> Create database... [green][DONE]")
    if db_recreated:
            with Progress(
                    TAB + "> Create tables... [IN PROGRESS]",
                    transient=True,
                    console=console
            ) as progress:
                _ = progress.add_task("Loading...")
                create_tables()
            print(TAB + "> Create tables... [green][DONE]")

    populate_database(console, build, update)


def main(args):
    console = Console(record=True)
    run(console,
        build=args.build,
        cases=args.cases,
        force=args.f,
        update=args.u)

def parse_args(parser):
    args = parser.parse_args()

    # Check path
    return args


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate final dataset files')
    parser.add_argument('--build', type=str, default="./build/echr_database/")
    parser.add_argument('--cases', type=str, default="unstructured/cases.json")
    parser.add_argument('-f', action='store_true')
    parser.add_argument('-u', action='store_true')
    args = parse_args(parser)

    main(args)
