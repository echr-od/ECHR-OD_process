#!/bin/python3
import argparse
import requests
import json
import os
import urllib3
from concurrent.futures import ThreadPoolExecutor

from echr.utils.folders import make_build_folder
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

urllib3.util.ssl_.DEFAULT_CIPHERS = 'ALL:@SECLEVEL=1'
BASE_URL = "https://hudoc.echr.coe.int/app/conversion/"
PERMA_URL = "https://hudoc.echr.coe.int/eng?i="
MAX_RETRY = 5


def get_documents(console, id_list, folder, update):
    """
        Get documents according to the specified list

        :param id_list: list of document id
        :type id_list: [str]
        :param folder: path where to save the documents
        :type folder: str
        :param update: overwrite existing documents
        :type: bool
    """

    def get_documents_step(doc_id, progress, task):
        if doc_id[1]:
            filename = "%s.docx" % (doc_id[0].strip())
        else:
            filename = "%s.pdf" % (doc_id[0].strip())
        filename = os.path.join(folder, filename)
        if update or not os.path.isfile(filename):
            if doc_id[1]:
                url = BASE_URL + "docx/?library=ECHR&filename=please_give_me_the_document.docx&id=" + doc_id[0].strip()
            else:
                url = BASE_URL + "docx/pdf?library=ECHR&filename=please_give_me_the_document.pdf&id=" + doc_id[
                    0].strip()
            for j in range(MAX_RETRY):
                try:
                    r = requests.get(url, stream=True, timeout=5)
                    if not r.ok:
                        raise Exception()
                    with open(filename, 'wb') as f:
                        for block in r.iter_content(1024):
                            f.write(block)
                    error = "\n| Request complete, see [cyan]%s" % (filename)
                    break
                except Exception as e:
                    try:  # Delete the incorrect file if it exists
                        os.remove(filename)
                    except OSError:
                        pass
                    log.debug(e)
                    error = '\n| ({}/{}) Failed to fetch document {}'.format(
                        j + 1, MAX_RETRY, doc_id[0])
                    error += '\n| URL: %s' % (url)
                    error += '\n| Permalink: %s' % (PERMA_URL + doc_id[0].strip())
                    progress.update(task, advance=0, error=error, doc=doc_id[0])
        else:
            error = "\n| Skip as document exists already"
        progress.update(task, advance=1, error=error, doc=doc_id[0])
    if id_list:
        with Progress(
            TAB + "> Downloading... [IN PROGRESS]\n",
            BarColumn(30),
            TimeRemainingColumn(),
            "| Fetching document of case [blue]{task.fields[doc]} [white]({task.completed}/{task.total})"
            "{task.fields[error]}",
                transient=True,
                console=console
        ) as progress:
            task = progress.add_task("Downloading...", total=len(id_list), error="", doc=id_list[0][0])
            f = lambda x: get_documents_step(x, progress, task)
            with ThreadPoolExecutor(16) as executor:
                executor.map(f, id_list)

        print(TAB + "> Downloading... [green][DONE]\n",)
    else:
        print(TAB + "> No documents to download")

def run(console, build, title, force=False, update=False):
    __console = console
    global print
    print = __console.print

    print(Markdown("- **Step configuration**"))
    input_file = os.path.join(build, 'raw', 'cases_info', 'raw_cases_info_all.json')
    output_folder = os.path.join(build, 'raw', 'judgments')
    print(TAB + '> Step folder: {}'.format(os.path.join(build, 'raw', 'judgments')))
    make_build_folder(console, output_folder, force, strict=False)
    id_list = []
    try:
        with open(input_file, 'r') as f:
            content = f.read()
            cases = json.loads(content)
            id_list = [(i['itemid'], i["application"].startswith("MS WORD")) for i in cases]
    except Exception as e:
        print(e)
        exit(1)

    print(Markdown("- **Get documents from HUDOC**"))
    get_documents(console, id_list, output_folder, update)


def main(args):
    console = Console(record=True)
    run(console, args.build, args.title, args.force, args.u)


def parse_args(parser):
    args = parser.parse_args()
    # Check path
    return args


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Filter and format ECHR cases information')
    parser.add_argument('--build', type=str, default="./build/echr_database/")
    parser.add_argument('--title', type=str)
    parser.add_argument('-f', action='store_true')
    parser.add_argument('-u', action='store_true')
    args = parse_args(parser)

    main(args)
