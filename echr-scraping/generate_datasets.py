import argparse
import requests
import json
import os
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

def main(args):
    try:
        if args.f:
            shutil.rmtree(args.output_folder)
        os.mkdir(args.output_folder)
    except Exception as e:
        print(e)
        exit(1)

    # Get the list of cases s.t. we have a BoW and TF-IDF representation
    files = [os.path.join(args.processed_folder, f) for f in listdir(args.processed_folder) if isfile(join(args.processed_folder, f)) if '_bow.txt' in f]
    id_list = [f.split('/')[-1].split('_')[0] for f in files]

    # Read the case info
    cases = []
    try:
        with open(args.cases_info, 'r') as f:
            content = f.read()
            cases = json.loads(content)
    except Exception as e:
        print(e)
        exit(1)

    # Filter the cases info to keep only the items in id_list
    #cases = [c for c in cases if c['itemid'] in id_list]

    keys = [
        "itemid",
        "respondent", 
        "Rank", 
        "applicability", 
        "decisiondate", 
        "doctypebranch", 
        "importance", 
        "introductiondate", 
        "judgementdate", 
        "originatingbody",
        "respondent",
        "respondentOrderEng",
        "separateopinion",
        "typedescription"

    ]

    keys_list = ["article", "documentcollectionid", "externalsources", "extractedappno", "kpthesaurus", "parties", "scl", "representedby"]

    feature_index = {k:i for i,k in enumerate(keys + keys_list)}
    feature_to_value = dict(zip(keys + keys_list, [None] * (len(keys) + len(keys_list))))
    for c in cases:
        #print(c)
        for k, v in c.iteritems():
            if k in keys:
                if feature_to_value[k] is None:
                    feature_to_value[k] = set()
                feature_to_value[k].add(v)
            if k in keys_list:
                if feature_to_value[k] is None:
                    feature_to_value[k] = set()
                feature_to_value[k].update(v)

    feature_to_encoded = {}
    count = 0
    for k, s in feature_to_value.iteritems():
    #    print(k, s, type(s))
        for v in s:
            if k in keys: 
                feature_to_encoded[u'{}={}'.format(k, v)] = count
            elif k in keys_list:
                feature_to_encoded[u'{}_has_{}'.format(k, v)] = count
            count += 1

    with open(os.path.join(args.output_folder, 'variables.json'), 'w') as f:
        json.dump(feature_index, f, indent=4)
        f.close()

    with open(os.path.join(args.output_folder, 'features.json'), 'w') as f:
        json.dump(feature_to_encoded, f, indent=4)
        f.close()

    # Encode conclusions
    outcomes = {}
    for i, c in enumerate(cases):
        ccl = c['conclusion_']
        for e in ccl:
            if e['type'] in ['violation', 'no-violation']:
                #print(c['itemid'], e)
                if e['article'] not in outcomes:
                    outcomes[e['article']] = {
                        'violation': 0,
                        'no-violation': 0,
                        'total': 0
                    }
                #if e['article'] == '8' and e['type'] == 'no-violation':
                #    print(c['docname'])
                outcomes[e['article']][e['type']] += 1
                outcomes[e['article']]['total'] += 1
        # Determine output

    outcomes = {k:v for k,v in outcomes.iteritems() if v['total'] > 100}

    encoded_outcomes = {}
    count = 1
    for i, o in outcomes.iteritems():
        encoded_outcomes[i] = count
        count +=1

    with open(os.path.join(args.output_folder, 'outcomes_variables.json'), 'w') as f:
        json.dump(encoded_outcomes, f, indent=4)
        f.close()

    dataset_size = 0
    with open(os.path.join(args.output_folder, 'full_descriptive.txt'), 'w') as f_d:
        with open(os.path.join(args.output_folder, 'full_outcomes.txt'), 'w') as f:
            for c in cases:
                encoded_case = []
                classes = []
                for e in c['conclusion_']:
                    if e['type'] in ['violation', 'no-violation']:
                        if 'article' in e and e['article'] in encoded_outcomes:
                            g = encoded_outcomes[e['article']]
                            classes.append('{}:{}'.format(g, 1 if e['type'] == 'violation' else 0))

                classes = list(set(classes))
                opposed_classes = any([e for e in classes if e.split(':')[0]+':'+ str(abs(1 - int(e.split(':')[-1]))) in classes])
                if len(classes) > 0 and not opposed_classes:
                    f.write('0:{} '.format(feature_to_encoded[u'{}={}'.format('itemid', c['itemid'])]))
                    f.write(' '.join(classes) + '\n')
                    for k, v in c.iteritems():
                        if k in keys: 
                            encoded_case.append('{}:{}'.format(feature_index[k], feature_to_encoded[u'{}={}'.format(k, v)]))
                        elif k in keys_list:
                            for e in v:
                                encoded_case.append('{}:{}'.format(feature_index[k], feature_to_encoded[u'{}_has_{}'.format(k, e)]))
                    f_d.write(' '.join(map(str, encoded_case)) + '\n')
                    dataset_size += 1
            f.close()
        f_d.close()

    statistics = {
        'multilabel':{
            'dataset_size': dataset_size
        }
    }
    with open(os.path.join(args.output_folder, 'statistics_datasets.json'), 'w') as f:
        json.dump(statistics, f, indent=4)
        f.close()

        #'''
def parse_args(parser):
    args = parser.parse_args()

    # Check path
    return args

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Filter and format ECHR cases information')
    parser.add_argument('--processed_folder', type=str, default="./processed_documents")
    parser.add_argument('--cases_info', type=str, default="./raw_cases_info.json")
    parser.add_argument('--output_folder', type=str, default="./datasets_documents")
    parser.add_argument('-f', action='store_true')
    args = parse_args(parser)

    main(args)
 