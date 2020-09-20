import argparse
import json
import copy
import os
import logging
from os import listdir
from os.path import isfile, join
from collections import Counter

from gensim import corpora, models, similarities
from nlp.data import load_text_file

from echr.utils.folders import make_build_folder
from echr.utils.logger import getlogger
from echr.utils.cli import TAB
from echr.utils.config import config
from rich.markdown import Markdown
from rich.console import Console
from rich.progress import (
    Progress,
    BarColumn,
    TimeRemainingColumn,
)

log = getlogger()

__console = Console(record=True)

def run(console, build, limit_tokens, processed_folder='all', force=False, update=False):
    __console = console
    global print
    print = __console.print

    input_file = os.path.join(build, 'cases_info/raw_cases_info_{}.json'.format(processed_folder))
    input_folder = os.path.join(build, 'raw_normalized_documents')
    output_folder = os.path.join(build, 'processed_documents', processed_folder)

    print(Markdown("- **Step configuration**"))
    print(TAB + '> Step folder: {}'.format(output_folder))
    make_build_folder(console, output_folder, force, strict=False)

    try:
        config()['steps']['normalize']['ngrams']
    except Exception as e:
        print('Cannot retrieve n-grams configuration. Details: {}'.format(e))
        exit(5)
    print(TAB + '> Read configuration [green][DONE]')

    cases_index = {}
    with open(input_file, 'r') as f:
        content = f.read()
        cases = json.loads(content)
        cases_index = {c['itemid']: i for i, c in enumerate(cases)}
        f.close()

    files = [os.path.join(input_folder, f) for f in listdir(input_folder) \
             if isfile(join(input_folder, f)) if '_normalized.txt' in f \
             and f.split('/')[-1].split('_normalized.txt')[0] in cases_index.keys()]
    raw_corpus = []
    corpus_id = []
    print(Markdown('- **Create dictionary**'))
    with Progress(
            TAB + "> Loading in memory... [IN PROGRESS]",
            BarColumn(30),
            TimeRemainingColumn(),
            "| Document [blue]{task.fields[doc]} [white]({task.completed}/{task.total})"
            "{task.fields[error]}",
            transient=True,
    ) as progress:
        task = progress.add_task("Loading...", total=len(files), error="",
                                 doc=files[0].split('/')[-1].split('_normalized.txt')[0])
        for i, p in enumerate(files):
            error = ""
            try:
                doc_id = p.split('/')[-1].split('_normalized.txt')[0]
                raw_corpus.append(load_text_file(p).split())
                corpus_id.append(doc_id)
            except Exception as e:
                error = '\n| {}'.format('Could not load the document')
                log.debug(p, e)
            progress.update(task, advance=1, error=error, doc=doc_id)
    print(TAB + "> Loading in memory... [green][DONE]")

    # data = json.load(open('./full_dictionary.txt'))
    f = [t for doc in raw_corpus for t in doc]
    f = Counter(f)
    # Load the raw dictionary
    f = f.most_common(int(limit_tokens))
    words = [w[0] for w in f]


    # dictionary = corpora.Dictionary([all_grams])
    print(TAB + '> Create dictionary')
    dictionary = corpora.Dictionary([words])
    dictionary.save(os.path.join(output_folder, 'dictionary.dict'))
    with open(os.path.join(output_folder, 'feature_to_id.dict'), 'w') as outfile:
        json.dump(dictionary.token2id, outfile, indent=4, sort_keys=True)
    corpus = [dictionary.doc2bow(text) for text in raw_corpus]
    print(Markdown('- **Create language models**'))
    with Progress(
            TAB + "> Create Bag of Word... [IN PROGRESS]",
            BarColumn(30),
            TimeRemainingColumn(),
            "| Document [blue]{task.fields[doc]} [white]({task.completed}/{task.total})"
            "{task.fields[error]}",
            transient=True,
    ) as progress:
        task = progress.add_task("Loading...", total=len(corpus), error="",
                                 doc=corpus_id[0])
        for i, doc in enumerate(corpus):
            error = ""
            filename = os.path.join(output_folder, '{}_bow.txt'.format(corpus_id[i]))
            # if update and not os.path.isfile(filename):
            with open(filename, 'w') as file:
                for f, v in doc:
                    file.write('{}:{} '.format(f, v))
            progress.update(task, advance=1, error=error, doc=corpus_id[i])
    print(TAB + "> Create Bag of Word... [green][DONE]")

    tfidf = models.TfidfModel(corpus)
    corpus_tfidf = tfidf[corpus]
    with Progress(
            TAB + "> Create TF-IDF... [IN PROGRESS]",
            BarColumn(30),
            TimeRemainingColumn(),
            "| Document [blue]{task.fields[doc]} [white]({task.completed}/{task.total})"
            "{task.fields[error]}",
            transient=True,
    ) as progress:
        task = progress.add_task("Loading...", total=len(corpus_tfidf), error="",
                                 doc=corpus_id[0])
        for i, doc in enumerate(corpus_tfidf):
            error = ""
            with open(os.path.join(output_folder, '{}_tfidf.txt'.format(corpus_id[i])), 'w') as file:
                for f, v in doc:
                    file.write('{}:{} '.format(f, v))
            progress.update(task, advance=1, error=error, doc=corpus_id[i])
    print(TAB + "> Create TF-IDF... [green][DONE]")


def main(args):
    console = Console(record=True)
    run(console, args.build, args.limit_tokens, force=args.f, update=args.u)


def parse_args(parser):
    args = parser.parse_args()
    args.limit_tokens = int(args.limit_tokens)
    # Check path
    return args


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Turn a collection of documents into a BoW and TF-IDF representation.')
    parser.add_argument('--build', type=str, default="./build/echr_database/")
    parser.add_argument('--processed_folder', type=str, default="all")
    parser.add_argument('--limit_tokens', type=int, default=5000)
    parser.add_argument('-f', action='store_true')
    parser.add_argument('-u', action='store_true')
    args = parse_args(parser)

    main(args)
