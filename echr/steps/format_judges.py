#!/usr/bin/python
import argparse
import json
import os
from os import path
from docx import Document

from echr.utils.folders import make_build_folder
from echr.utils.logger import getlogger
from echr.utils.cli import TAB
from rich.markdown import Markdown
from rich.console import Console

log = getlogger()

JUDGE_LIST = './data/List_judges_since_1959_BIL.docx'


def extract_judge_list(docx_file):
    doc = Document(docx_file)
    judges_per_country = {}
    country = None
    for para in doc.paragraphs:
        content = para.text
        if not content:
            continue
        if content.upper() == content and not any(char.isdigit() for char in content):
            country = content.split('/')[0].title().strip().replace(' And ', ' and ').replace(' Of ', ' of ')
            if country not in judges_per_country:
                judges_per_country[country] = {}
        else:
            if country is None:
                continue
            if content and content[0].isdigit():
                tokens = content.split()
                start_year = tokens[0]
                if tokens[2].isdigit():
                    full_name = ' '.join(tokens[3:])
                    end_year = tokens[2]
                    name_index = ' '.join(
                        [n for n in tokens[3:] if (n.upper() == n or n.startswith('Mc')) and '.' not in n])
                else:
                    full_name = ' '.join(tokens[2:])
                    end_year = None
                    name_index = ' '.join(
                        [n for n in tokens[2:] if (n.upper() == n or n.startswith('Mc')) and '.' not in n])
                if len(name_index) < 2 or name_index.startswith('/'):
                    continue
                if '(P' in full_name:
                    full_name = full_name.split(' (')[0]
                judges_per_country[country][name_index.upper().replace('-', ' ')] = {
                    'start': start_year,
                    'end': end_year,
                    'full_name': full_name
                }
    return judges_per_country


def run(console, build, title, doc_ids=None, force=False):
    __console = console
    global print
    print = __console.print

    print(Markdown("- **Step configuration**"))
    output_folder = path.join(build, 'raw', )
    print(TAB + '> Step folder: {}'.format(path.join(build, 'judges')))
    make_build_folder(console, output_folder, force, strict=False)

    print(Markdown("- **Extract of judges**"))
    judges_per_country = extract_judge_list(JUDGE_LIST)

    with open(path.join(output_folder, 'judges_per_country.json'), 'w') as outfile:
        json.dump(judges_per_country, outfile, indent=4, sort_keys=True)

    print(TAB + "> Extract the list of judges [green][DONE]", )


def main(args):
    console = Console(record=True)
    run(console, args.build, args.title, args.doc_ids, args.force)


def parse_args(parser):
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Extract the list of judges')
    parser.add_argument('--build', type=str, default="./build/echr_database/")
    parser.add_argument('--title', type=str)
    parser.add_argument('--doc_ids', type=str, default=None, nargs='+')
    parser.add_argument('-f', action='store_true')
    args = parse_args(parser)

    main(args)
