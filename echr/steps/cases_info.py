#!/usr/bin/python3
import argparse
import requests
import json
import os
import time
import urllib3
from concurrent.futures import ThreadPoolExecutor

from echr.utils.logger import getlogger
from echr.utils.cli import StatusColumn, TAB
from echr.utils.folders import make_build_folder
from rich.markdown import Markdown
from rich.console import Console
from rich.progress import (
    TextColumn,
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
BASE_URL = "http://hudoc.echr.coe.int/app/query/results" \
           "?query=((((((((((((((((((((%20contentsitename%3AECHR%20AND%20(NOT%20(doctype%3DPR%20OR%20" \
           "doctype%3DHFCOMOLD%20OR%20doctype%3DHECOMOLD)))%20XRANK(cb%3D14)%20doctypebranch%3AGRANDCHAMBER" \
           ")%20XRANK(cb%3D13)%20doctypebranch%3ADECGRANDCHAMBER)%20XRANK(cb%3D12)%20doctypebranch%3ACHAMBER)" \
           "%20XRANK(cb%3D11)%20doctypebranch%3AADMISSIBILITY)%20XRANK(cb%3D10)%20doctypebranch%3ACOMMITTEE)" \
           "%20XRANK(cb%3D9)%20doctypebranch%3AADMISSIBILITYCOM)%20XRANK(cb%3D8)%20doctypebranch%3ADECCOMMISSION)" \
           "%20XRANK(cb%3D7)%20doctypebranch%3ACOMMUNICATEDCASES)%20XRANK(cb%3D6)%20doctypebranch%3ACLIN)%20" \
           "XRANK(cb%3D5)%20doctypebranch%3AADVISORYOPINIONS)%20XRANK(cb%3D4)%20doctypebranch%3AREPORTS)%20" \
           "XRANK(cb%3D3)%20doctypebranch%3AEXECUTION)%20XRANK(cb%3D2)%20doctypebranch%3AMERITS)%20XRANK(cb%3D1)" \
           "%20doctypebranch%3ASCREENINGPANEL)%20XRANK(cb%3D4)%20importance%3A1)%20XRANK(cb%3D3)%20importance%3A2)" \
           "%20XRANK(cb%3D2)%20importance%3A3)%20XRANK(cb%3D1)%20importance%3A4)%20XRANK(cb%3D2)%20" \
           "languageisocode%3AENG)%20XRANK(cb%3D1)%20languageisocode%3AFRE" \
           "&select={}&sort=&rankingModelId=4180000c-8692-45ca-ad63-74bc4163871b".format(','.join(fields))
LENGTH = 500  # maximum number of items per request


def determine_max_documents(base_url, default_value):
    """
        Automatically determine the number of available documents in HUDOC

        :param default_value: fallback value
        :type default_value: [int]
    """
    url = base_url + "&start={}&length={}".format(0, 1)
    for i in range(MAX_RETRY):
        try:
            r = requests.get(url)
            if not r.ok:
                print('\t({}/{}) Failed to fetch max document numbers'.format(i + 1, MAX_RETRY))
                continue
            else:
                output = json.loads(r.content)
                return 0, int(output['resultcount'])
        except Exception as e:
            __console.print_exception()
            log.error(e)
            print(TAB + '({}/{}) Failed to fetch max document numbers'.format(i + 1, MAX_RETRY))
    print(TAB + "[bold yellow]:warning: Fallback to the default number of cases: {}".format(default_value))
    max_documents = default_value
    return 1, max_documents


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
    length = min(LENGTH, max_documents)
    if length <= 0:
        return 2

    def get_cases_info_step(start, length, progress, task):
        error = ""
        file_path = os.path.join(path, "{}.json".format(start))
        failed_to_get_some_cases = False
        with open(file_path, 'wb') as f:
            url = base_url + "&start=%d&length=%d" % (start, length)
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
                    log.error('({}/{}) Failed to fetch information {} to {}'.format(
                        i + 1, MAX_RETRY, start, start + length))
                    error = '\n| ({}/{}) Failed to fetch information {} to {}'.format(
                        i + 1, MAX_RETRY, start, start + length)
                    time.sleep(0.001)
                if error:
                    progress.update(task, advance=0, error=error)
            else:
                failed_to_get_some_cases = True
        progress.update(task, advance=length, to_be_completed=start + 2 * length)
        return failed_to_get_some_cases


    with Progress(
            TAB + "> Downloading... [IN PROGRESS]\n",
            BarColumn(30),
            TimeRemainingColumn(),
            "| ({task.completed}/{task.total}) Fetching information from cases {task.completed} to {task.fields[to_be_completed]}"
            "{task.fields[error]}",
            transient=True,
            console=console
    ) as progress:
        task = progress.add_task("Downloading...", total=max_documents, to_be_completed=length, error="")
        f = lambda x: get_cases_info_step(x, length, progress, task)
        with ThreadPoolExecutor(16) as executor:
            results = list(executor.map(f, range(0, max_documents, length)))
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

def run(console, build, max_documents=-1, force=False):
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
    if max_documents == -1:
        print(TAB + "> The total number of documents is not provided")
        with Progress(
            TextColumn(TAB + "> Querying HUDOC...", justify="right"),
            StatusColumn({
                    None: '[IN PROGRESS]',
                    0: '[green] [DONE]',
                    1: '[red] [FAILED]'
            }),
            transient=True,
            console=console
        ) as progress:
            task = progress.add_task("Get total number of documents")
            while not progress.finished:
                rc, max_documents = determine_max_documents(BASE_URL, 144579)  # v1.0.0 value
                progress.update(task, rc=rc)
    print(TAB + "> The total number of documents to retrieve: {}".format(max_documents))
    print(Markdown("- **Get case information from HUDOC**"))
    get_case_info(console, BASE_URL, max_documents, output_folder)


def main(args):
    console = Console(record=True)
    run(console, args.build, args.max_documents, args.f)


def parse_args(parser):
    return parser.parse_args()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Retrieve ECHR cases information')
    parser.add_argument('--build', type=str, default="./build/echr_database/")
    parser.add_argument('--max_documents', type=int, default=-1)
    parser.add_argument('-f', action='store_true')
    args = parse_args(parser)

    main(args)
