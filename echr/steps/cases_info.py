#!/usr/bin/python3
import argparse
import requests
import json
import os
import time
import urllib3
from concurrent.futures import ThreadPoolExecutor
import datetime

from echr.utils.logger import getlogger
from echr.utils.cli import TAB
from echr.utils.folders import make_build_folder
from rich.markdown import Markdown
from rich.console import Console
from rich.progress import (
    Progress,
    BarColumn,
    TimeRemainingColumn,
)

log = getlogger()
__console = Console(record=True)

urllib3.util.ssl_.DEFAULT_CIPHERS = 'ALL:@SECLEVEL=1'
MAX_RETRY = 5

# Fields to retrieve
fields = [
    "sharepointid",
    "Rank",
    "itemid",
    "docname",
    "doctype",
    "application",
    "appno",
    "conclusion",
    "importance",
    "originatingbody",
    "typedescription",
    "kpdate",
    "kpdateAsText",
    "documentcollectionid",
    "documentcollectionid2",
    "languageisocode",
    "extractedappno",
    "isplaceholder",
    "doctypebranch",
    "respondent",
    "respondentOrderEng",
    "ecli",
    "article",
    "applicability",
    "decisiondate",
    "externalsources",
    "introductiondate",
    "issue",
    "judgementdate",
    "kpthesaurus",
    "meetingnumber",
    "representedby",
    "separateopinion",
    "scl"
]

BASE_URL = 'https://hudoc.echr.coe.int/app/query/results?query=contentsitename:ECHR' \
     ' AND (NOT (doctype=PR OR doctype=HFCOMOLD OR doctype=HECOMOLD)) AND ((languageisocode="ENG"))' \
     ' AND (kpdate>="YEAR-01-01T00:00:00.0Z" AND kpdate<="YEAR_1-01-01T00:00:00.0Z")' \
     ' AND ((organisations:"ECHR"))&select={}&sort=&start=0&length=10000&rankingModelId=11111111-0000-0000-0000-000000000000'.format(','.join(fields))
LENGTH = 10_000  # maximum number of items per request
YEARS = range(1959, datetime.date.today().year+1)


def get_case_info(console, base_url, max_documents, path):
    """
        Get case information from HUDOC

        :param base_url: base url to query for documents
        :type base_url: string
        :param: max_documents: maximal number of documents to retrieve
        :type: int
        :param: path: path to store the information
        :type: str
    """
    def get_cases_info_step(year, progress, task):
        error = ""
        file_path = os.path.join(path, "{}.json".format(year))
        failed_to_get_some_cases = False
        with open(file_path, 'wb') as f:
            url = base_url.replace('YEAR_1', str(year+1)).replace('YEAR', str(year))
            for i in range(MAX_RETRY):
                error = ""
                try:
                    r = requests.get(url, stream=True, timeout=10)
                    if not r.ok:
                        raise Exception()
                    for block in r.iter_content(1024):
                        f.write(block)
                    break
                except:
                    try:  # Delete the incorrect file if it exists
                        os.remove(file_path)
                    except OSError:
                        pass
                    __console.print_exception()
                    log.error('({}/{}) Failed to fetch information for year {}'.format(
                        i + 1, MAX_RETRY, year))
                    error = '\n| ({}/{}) Failed to fetch information for year {}'.format(
                        i + 1, MAX_RETRY, year)
                    time.sleep(0.001)
                if error:
                    progress.update(task, advance=0, error=error)
            else:
                failed_to_get_some_cases = True
        progress.update(task, advance=1, to_be_completed=len(YEARS), year=year)
        return failed_to_get_some_cases

    with Progress(
            TAB + "> Downloading... [IN PROGRESS]\n",
            BarColumn(30),
            TimeRemainingColumn(),
            "| ({task.completed}/{task.total}) Fetching cases information for year {task.fields[year]}"
            "{task.fields[error]}",
            transient=True,
            console=console
    ) as progress:
        task = progress.add_task("Downloading...", total=len(YEARS), to_be_completed=len(YEARS), year=YEARS[0], error="")
        f = lambda x: get_cases_info_step(x, progress, task)
        with ThreadPoolExecutor(16) as executor:
            results = list(executor.map(f, YEARS))
    failed_to_get_some_cases = all(results)
    if failed_to_get_some_cases:
        print(TAB + '> Downloading... [yellow][WARNING]')
        print(TAB + "[bold yellow]:warning: Some information could not be downloaded")
        print(TAB + "  [bold yellow]THE FINAL DATABASE WILL BE INCOMPLETE!")
        print(TAB + "  [bold yellow]Use --strict flag to exit on single failure")
        return failed_to_get_some_cases
    else:
        print(TAB + '> Downloading... [green][DONE]')
        return 0


def run(console, build, title, doc_ids=None, max_documents=-1, force=False):
    """
        Get case information from HUDOC

        :param build: build path
        :type string
        :param: max_documents: maximal number of documents to retrieve
        :type: int
        :param: force: delete and recreate the folder
        :type: bool
    """
    __console = console
    global print
    print = __console.print

    print(Markdown("- **Step configuration**"))
    output_folder = os.path.join(build, 'raw', 'raw_cases_info')
    print(TAB + '> Step folder: {}'.format(output_folder))
    make_build_folder(console, output_folder, force, strict=False)

    print(Markdown("- **Determining the number cases**"))
    if doc_ids:
        print(TAB + "> Doc ids given")
    print(Markdown("- **Get case information from HUDOC**"))
    get_case_info(console, BASE_URL, max_documents, output_folder)


def main(args):
    console = Console(record=True)
    run(console, args.build, args.title, args.doc_ids, args.max_documents, args.f)


def parse_args(parser):
    return parser.parse_args()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Retrieve ECHR cases information')
    parser.add_argument('--build', type=str, default="./build/echr_database/")
    parser.add_argument('--title', type=str)
    parser.add_argument('--doc_ids', type=str, default=None, nargs='+')
    parser.add_argument('--max_documents', type=int, default=-1)
    parser.add_argument('-f', action='store_true')
    args = parse_args(parser)
    main(args)
