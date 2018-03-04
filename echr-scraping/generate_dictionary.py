import argparse
import requests
import json
import copy
import os
import logging
from time import sleep
from os import listdir
from os.path import isfile, join
import re
import shutil
from docx import Document
from docx.shared import Inches
from docx.text.run import Run
import zipfile
from collections import Counter

from gensim import corpora, models, similarities

from NLP.data import load_text_file, load_CSV, data_transformations, match_city, department_name, max_n_gram, filter_per_inhabitants
from NLP.preprocessing import rectify_missing_space, prepareText, frequencies, generateNGrams

from nltk.tokenize import word_tokenize
from nltk.util import ngrams

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


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
    #print('normalized_tokens', normalized_tokens)
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
        log.info('No configuration specified, uses the default one')
    freq = {1: 1, 2: 1, 3: 1, 4: 1}

    for k in freq:
        output_file = 'tokens_{}grams.txt'.format(k)
        p = os.path.join(path, output_file)
        if not force:
            if os.path.isfile(p):
                raise Exception("The file {} already exists!".format(p))

    allgrams = frequencies(original_tokens, n=len(freq), minlimits=freq)
    
    return allgrams


def main(args):

    config = None
    try:
        with open('config/config.json') as data:
            config = json.load(data)
            # Basic config validation
            if 'ngrams' not in config:
                raise Exception('Section "ngrams" missing from configuration file')
            else:
                for k in copy.deepcopy(config['ngrams']):
                    config['ngrams'][int(k)] = config['ngrams'][k]
                    del config['ngrams'][k]
    except Exception as e:
        print('Cannot load configuration file. Details: {}'.format(e))
        exit(5)


    try:
        if args.f:
            shutil.rmtree(args.output_folder)
        os.mkdir(args.output_folder)
    except Exception as e:
        print(e)
        exit(1)

    files = sorted([os.path.join(args.input_folder, f) for f in listdir(args.input_folder) if isfile(join(args.input_folder, f)) if '_text_without_conclusion.txt' in f])
    raw_corpus = []
    corpus_id = []
    for i, p in enumerate(files):
        try:
            print('Load document {}/{}'.format(i, len(files)))
            doc_id = p.split('/')[-1].split('_text_without_conclusion.txt')[0]
            raw_corpus.append(load_text_file(p))
            corpus_id.append(doc_id)
        except Exception as e:
            print(p, e)

    normalized_tokens = []
    try:
        for i, doc in enumerate(raw_corpus):
            print('Normalize document {}/{}'.format(i, len(raw_corpus)))
            normalized_tokens.append(normalized_step(doc, force=args.f, lemmatization=True))
    except Exception as e:
        print('Could not normalized the tokens. Details: {}'.format(e))
        exit(40)

    all_grams = []
    doc_grammed = []
    try:
        for i, doc in enumerate(normalized_tokens):
            print('Calculate ngrams for document {}/{}'.format(i, len(raw_corpus)))
            grams = ngram_step(doc, config['ngrams'], force=args.f)
            merged = []
            for g in grams.values():
                merged.extend(g)
            doc_grammed.append(merged)
            all_grams.extend(merged)
            #print(grams.values())
    except Exception as e:
        print(e)

    f = Counter(all_grams)
    with open('./full_dictionary.txt', 'w') as outfile:
        json.dump(f, outfile, indent=4, sort_keys=True)

    for i, doc in enumerate(doc_grammed):
        with open(os.path.join(args.output_folder, '{}_normalized.txt'.format(corpus_id[i])), 'a') as file:
            file.write(' '.join(doc))

def parse_args(parser):
    args = parser.parse_args()

    # Check path
    return args

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Turn a collection of documents into a BoW and TF-IDF representation.')
    parser.add_argument('--output_folder', type=str, default="./raw_normalized_documents")
    parser.add_argument('--input_folder', type=str, default="./preprocessed_documents")
    parser.add_argument('-f', action='store_true')
    args = parse_args(parser)

    main(args)
 