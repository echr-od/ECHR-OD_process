import argparse
import copy
import json
import logging
import os
from os import listdir
from os.path import isfile, join
import shutil
import sys
from collections import Counter

from gensim import corpora, models, similarities
from nlp.data import load_text_file
from nlp.preprocessing import prepareText, frequencies
from nltk.tokenize import word_tokenize

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

def normalized_step(tokens, path='./', force=False, lemmatization=True):
    """
        Normalize the tokens

        :param tokens: list of strings
        :type tokens: [str]
        :param path: path to write the output in
        :type path: str

        :return: normalized tokens
        :rtype: [str]
    """
    normalized_tokens = prepareText(tokens, lemmatization)
    normalized_tokens = [t[0] for t in normalized_tokens]
    # print('normalized_tokens', normalized_tokens)
    return normalized_tokens


def ngram_step(original_tokens, freq=None, path='./', force=False):
    """
        Calculate the ngrams

        :param original_tokens: list of tokens
        :type original_tokens: [[str]]
        :param freq: rules to extract and filter ngrams
        :type freq: dict
        :param path: path to write the output in
        :type path: str

        :return: dictionary of ngrams indexed by n
        :rtype: dict
    """
    if freq is None:
        logging.info('No configuration specified, uses the default one')
        freq = {1: 1, 2: 1, 3: 1, 4: 1}

    for k in freq:
        output_file = 'tokens_{}grams.txt'.format(k)
        p = os.path.join(path, output_file)
        if not force:
            if os.path.isfile(p):
                raise Exception("The file {} already exists!".format(p))

    allgrams = frequencies(original_tokens, n=len(freq), minlimits=freq)
    return allgrams


def run(console, build, force=False, update=False):
    __console = console
    global print
    print = __console.print

    print(Markdown("- **Step configuration**"))
    input_folder = os.path.join(build, 'raw', 'preprocessed_documents')
    output_folder = os.path.join(build, 'raw', 'normalized_documents')
    ngrams_config = {}
    try:
        ngrams_config = config()['steps']['normalize']['ngrams']
    except Exception as e:
        print('Cannot retrieve n-grams configuration. Details: {}'.format(e))
        exit(5)

    print(TAB + '> Step folder: {}'.format(output_folder))
    make_build_folder(console, output_folder, force, strict=False)

    files = sorted([os.path.join(input_folder, f) for f in listdir(input_folder) if isfile(join(input_folder, f)) if
                    '_text_without_conclusion.txt' in f])
    raw_corpus = []
    corpus_id = []
    print(Markdown('- **Load documents**'))
    with Progress(
            TAB + "> Loading in memory... [IN PROGRESS]",
            BarColumn(30),
            TimeRemainingColumn(),
            "| Document [blue]{task.fields[doc]} [white]({task.completed}/{task.total})"
            "{task.fields[error]}",
            transient=True,
            console=console
    ) as progress:
        task = progress.add_task("Loading...", total=len(files), error="",
                                 doc=files[0].split('/')[-1].split('_text_without_conclusion.txt')[0])
        for i, p in enumerate(files):
            error = ""
            doc_id = p.split('/')[-1].split('_text_without_conclusion.txt')[0]
            try:
                raw_corpus.append(load_text_file(p))
                corpus_id.append(doc_id)
            except Exception as e:
                error = '\n| {}'.format('Could not load the document')
                log.debug(p, e)
            progress.update(task, advance=1, error=error, doc=doc_id)
    print(TAB + "> Loading in memory... [green][DONE]")

    normalized_tokens = []
    print(Markdown('- **Generate language model**'))
    try:
        with Progress(
                TAB + "> Normalize... [IN PROGRESS]\n",
                BarColumn(30),
                TimeRemainingColumn(),
                "| Document [blue]{task.fields[doc]} [white]({task.completed}/{task.total})"
                "{task.fields[error]}",
                transient=True,
                console=console
        ) as progress:
            task = progress.add_task("Compute tokens...", total=len(raw_corpus), error="", doc=corpus_id[0])
            for i, doc in enumerate(raw_corpus):
                filename = os.path.join(output_folder, '{}_normalized.txt'.format(corpus_id[i]))
                if not update or not os.path.isfile(filename):
                    normalized_tokens.append(normalized_step(doc, force=force, lemmatization=True))
                else:
                    with open(filename, 'r') as f:
                        normalized_tokens.extend(f.read().split())
                        f.close()
                progress.update(task, advance=1, error=error, doc=corpus_id[i])
    except Exception as e:
        print(TAB + '[bold red]:double_exclamation_mark: Could not normalized the tokens. Details: {}'.format(e))
        exit(40)
    print(TAB + "> Normalize... [green][DONE]")

    all_grams = []
    doc_grammed = []
    try:
        with Progress(
                TAB + "> Compute ngrams... [IN PROGRESS]\n",
                BarColumn(30),
                TimeRemainingColumn(),
                "| Document [blue]{task.fields[doc]} [white]({task.completed}/{task.total})"
                "{task.fields[error]}",
                transient=True,
                console=console
        ) as progress:
            task = progress.add_task("Compute tokens...", total=len(corpus_id), error="", doc=corpus_id[0])
            for i, doc in enumerate(normalized_tokens):
                error = ""
                filename = os.path.join(output_folder, '{}_normalized.txt'.format(corpus_id[i]))
                if not update or not os.path.isfile(filename):
                    grams = ngram_step(doc, ngrams_config, force=force)
                    merged = []
                    for g in grams.values():
                        merged.extend(g)
                    doc_grammed.append(merged)
                    all_grams.extend(merged)
                else:
                    error = "\n| Load document as already normalized."
                    with open(filename, 'r') as f:
                        all_grams.extend(f.read().split())
                        doc_grammed.append(None)
                        f.close()
                progress.update(task, advance=1, error=error, doc=corpus_id[i])
    except Exception as e:
        console.print_exception()
    print(TAB + "> Compute ngrams... [green][DONE]")

    f = Counter(all_grams)
    with open(os.path.join(output_folder, 'full_dictionary.txt'), 'w') as outfile:
        json.dump(f, outfile, indent=4, sort_keys=True)
    print(TAB + '> Save the full dictionary [green][DONE]')


    with Progress(
            TAB + "> Save normalized documents... [IN PROGRESS]\n",
            BarColumn(30),
            TimeRemainingColumn(),
            "| Document [blue]{task.fields[doc]} [white]({task.completed}/{task.total})"
            "{task.fields[error]}",
            transient=True,
            console=console
    ) as progress:
        task = progress.add_task("Compute tokens...", total=len(doc_grammed), error="", doc=corpus_id[0])
        for i, doc in enumerate(doc_grammed):
            if doc is not None:
                with open(os.path.join(output_folder, '{}_normalized.txt'.format(corpus_id[i])), 'a') as file:
                    file.write(' '.join(doc))
            progress.update(task, advance=1, error=error, doc=corpus_id[i])
    print(TAB + '> Save normalized documents... [green][DONE]')


def main(args):
    console = Console(record=True)
    run(console, args.build, args.force, args.u)


def parse_args(parser):
    args = parser.parse_args()

    # Check path
    return args


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Turn a collection of documents into a BoW and TF-IDF representation.')
    parser.add_argument('--build', type=str, default="./build/echr_database/")
    parser.add_argument('-f', action='store_true')
    parser.add_argument('-u', action='store_true')
    args = parse_args(parser)

    main(args)
