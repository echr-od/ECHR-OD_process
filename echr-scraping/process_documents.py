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
import sys
from collections import Counter

from gensim import corpora, models, similarities

from nlp.data import load_text_file, load_CSV, data_transformations, match_city, department_name, max_n_gram, filter_per_inhabitants
from nlp.preprocessing import rectify_missing_space, prepareText, frequencies, generateNGrams

from nltk.tokenize import word_tokenize
from nltk.util import ngrams

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

CONFIG_FILE = './config/config.json'

def main(args):
    input_file = os.path.join(args.build, 'cases_info/raw_cases_info.json')
    input_folder = os.path.join(args.build, 'raw_normalized_documents')
    output_folder = os.path.join(args.build, 'processed_documents', args.processed_folder)
    print('# Read configuration')
    config = None
    try:
        with open(CONFIG_FILE) as data:
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

    cases_index = {}
    with open(input_file, 'r') as f:
        content = f.read()
        cases = json.loads(content)
        cases_index = {c['itemid']:i for i,c in enumerate(cases)}
        f.close()


    if not args.u:
        try:
            if args.f:
                shutil.rmtree(output_folder)
        except Exception as e:
            print(e)

        try:
            os.makedirs(output_folder)
        except Exception as e:
            print(e)

    update = args.u
    files = [os.path.join(input_folder, f) for f in listdir(input_folder) \
        if isfile(join(input_folder, f)) if '_normalized.txt' in f \
        and f.split('/')[-1].split('_normalized.txt')[0] in cases_index.keys()]
    raw_corpus = []
    corpus_id = []
    print('# Load documents')
    for i, p in enumerate(files):
        try:
            sys.stdout.write('\r - Load document {}/{}'.format(i+1, len(files)))
            doc_id = p.split('/')[-1].split('_normalized.txt')[0]
            raw_corpus.append(load_text_file(p).split())
            corpus_id.append(doc_id)
        except Exception as e:
            print(p, e)
    print('')
    #data = json.load(open('./full_dictionary.txt'))
    f = [t for doc in raw_corpus for t in doc]
    f = Counter(f)
    # Load the raw dictionnary
    f = f.most_common(args.limit_tokens)
    words = [w[0] for w in f]
    #print(words)
    #print(len(doc_grammed[0]), len(doc_grammed[1]))
    #print(len(all_grams), len(f))

    #dictionary = corpora.Dictionary([all_grams])
    print('# Create dictionary')
    dictionary = corpora.Dictionary([words])
    dictionary.save(os.path.join(output_folder, 'dictionary.dict'))
    with open(os.path.join(output_folder, 'feature_to_id.dict'), 'w') as outfile:
        json.dump(dictionary.token2id, outfile, indent=4, sort_keys=True)
    #print(dictionary.token2id)
    corpus = [dictionary.doc2bow(text) for text in raw_corpus]
    print('# Create Bag of Words')
    for i, doc in enumerate(corpus):
        filename = os.path.join(output_folder, '{}_bow.txt'.format(corpus_id[i]))
        #if update and not os.path.isfile(filename):
        with open(filename, 'w') as file:
            for f, v in doc:
                file.write('{}:{} '.format(f, v))


    tfidf = models.TfidfModel(corpus)
    corpus_tfidf = tfidf[corpus]
    print('# Create TFIDF')
    for i, doc in enumerate(corpus_tfidf):
        with open(os.path.join(output_folder, '{}_tfidf.txt'.format(corpus_id[i])), 'w') as file:
            for f, v in doc:
                file.write('{}:{} '.format(f, v))

def parse_args(parser):
    args = parser.parse_args()

    # Check path
    return args

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Turn a collection of documents into a BoW and TF-IDF representation.')
    parser.add_argument('--build', type=str, default="./build/echr_database/")
    parser.add_argument('--processed_folder', type=str, default="all")
    parser.add_argument('--limit_tokens', type=int, default="100000")
    parser.add_argument('-f', action='store_true')
    parser.add_argument('-u', action='store_true')
    args = parse_args(parser)

    main(args)
 