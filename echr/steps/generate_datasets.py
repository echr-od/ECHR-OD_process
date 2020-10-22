import argparse
import json
import os
from os import listdir
from os.path import isfile, join
import shutil

from echr.utils.folders import make_build_folder
from echr.utils.cli import StatusColumn, TAB
from rich.markdown import Markdown
from rich.console import Console
from rich.table import Table
from rich.progress import (
    Progress,
    BarColumn,
    TimeRemainingColumn,
)


def generate_dataset(cases, keys, keys_list, encoded_outcomes, feature_index, feature_to_encoded, output_path, name,
                     offset, processed_folder, filter_classes=None, force=False):
    output_path = output_path

    dataset_size = 0
    dataset_full_doc_id = []
    min_feature = 1000000
    max_feature = 0
    avg_feature = 0
    prevalence = {}
    outcome_distribution = {}
    conclusion_key = 'conclusion' if name != 'multiclass' else 'mc_conclusion'
    with open(os.path.join(output_path, 'descriptive.txt'), 'w') as f_d, \
            open(os.path.join(output_path, 'BoW.txt'), 'w') as f_b, \
            open(os.path.join(output_path, 'TF_IDF.txt'), 'w') as f_t, \
            open(os.path.join(output_path, 'descriptive+BoW.txt'), 'w') as f_db, \
            open(os.path.join(output_path, 'descriptive+TF_IDF.txt'), 'w') as f_dt, \
            open(os.path.join(output_path, 'outcomes.txt'), 'w') as f:
        for c in cases:
            nb_features = 0
            encoded_case = []
            classes = []
            for e in c[conclusion_key]:
                if e['type'] in ['violation', 'no-violation']:
                    if 'article' in e and e['article'] in encoded_outcomes:
                        g = encoded_outcomes[e['article']]
                        if filter_classes is None or e['article'] in filter_classes:
                            classes.append('{}:{}'.format(g, 1 if e['type'] == 'violation' else 0))
            classes = list(set(classes))
            opposed_classes = any(
                [e for e in classes if e.split(':')[0] + ':' + str(abs(1 - int(e.split(':')[-1]))) in classes])
            if len(classes) > 0 and not opposed_classes:
                f.write('0:{} '.format(feature_to_encoded[u'{}={}'.format('itemid', c['itemid'])]))
                f.write(' '.join(classes) + '\n')
                for e in c[conclusion_key]:
                    if e['type'] in ['violation', 'no-violation']:
                        if 'article' in e and e['article'] in encoded_outcomes:
                            if filter_classes is None or e['article'] in filter_classes:
                                if e['article'] not in outcome_distribution:
                                    outcome_distribution[e['article']] = {'violation': 0, 'no-violation': 0}
                                outcome_distribution[e['article']][e['type']] += 1
                                if name != 'multilabel':
                                    break
                for k, v in c.items():
                    if k in keys:
                        encoded_case.append('{}:{}'.format(feature_index[k], feature_to_encoded[u'{}={}'.format(k, v)]))
                    elif k in keys_list:
                        for e in v:
                            encoded_case.append(
                                '{}:{}'.format(feature_index[k], feature_to_encoded[u'{}_has_{}'.format(k, e)]))

                nb_features += len(encoded_case)
                f_d.write(' '.join(map(str, encoded_case)) + '\n')
                f_db.write(' '.join(map(str, encoded_case)) + ' ')
                f_dt.write(' '.join(map(str, encoded_case)) + ' ')
                dataset_size += 1
                dataset_full_doc_id.append(c['itemid'])
                with open(os.path.join(processed_folder, 'bow', '{}_bow.txt'.format(c['itemid'])), 'r') as bow_doc:
                    bow = bow_doc.read()
                    bow = bow.split()
                    bow = ['{}:{}'.format(offset + int(b.split(':')[0]), b.split(':')[1]) for b in bow]
                    f_db.write(' '.join(map(str, bow)) + ' \n')
                    f_b.write(' '.join(map(str, bow)) + ' \n')
                    nb_features += len(bow)
                with open(os.path.join(processed_folder, 'tfidf', '{}_tfidf.txt'.format(c['itemid'])), 'r') as tfidf_doc:
                    tfidf = tfidf_doc.read()
                    tfidf = tfidf.split()
                    tfidf = ['{}:{}'.format(offset + int(b.split(':')[0]), b.split(':')[1]) for b in tfidf]
                    f_t.write(' '.join(map(str, tfidf)) + ' \n')
                    f_dt.write(' '.join(map(str, tfidf)) + ' \n')

                max_feature = nb_features if nb_features > max_feature else max_feature
                min_feature = nb_features if nb_features < min_feature else min_feature
                avg_feature += nb_features

        f.close()
        f_db.close()
        f_dt.close()
        f_d.close()

    with open(os.path.join(processed_folder, 'feature_to_id.dict'), 'r') as d, open(
            os.path.join(output_path, 'features_text.json'), 'w') as f:
        features = json.loads(d.read())
        for k in features.keys():
            features[k] = int(features[k]) + offset
        json.dump(features, f, indent=4)
        d.close()
        f.close()

    statistics = {
        name: {
            'dataset_size': dataset_size,
            'min_feature': min_feature,
            'max_feature': max_feature,
            'avg_feature': float(avg_feature) / dataset_size if dataset_size > 0 else 0,
            'prevalence': outcome_distribution
        }
    }

    for cl, el in statistics[name]['prevalence'].items():
        statistics[name]['prevalence'][cl]['class_normalized'] = 1. * statistics[name]['prevalence'][cl][
            'violation'] / (statistics[name]['prevalence'][cl]['violation'] + statistics[name]['prevalence'][cl][
            'no-violation'])
        statistics[name]['prevalence'][cl]['no-violation_normalized'] = 1. * statistics[name]['prevalence'][cl][
            'no-violation'] / dataset_size
        statistics[name]['prevalence'][cl]['violation_normalized'] = 1. * statistics[name]['prevalence'][cl][
            'violation'] / dataset_size

    with open(os.path.join(output_path, 'statistics_datasets.json'), 'w') as f:
        json.dump(statistics, f, indent=4)
        f.close()

    with open(os.path.join(output_path, 'variables_descriptive.json'), 'w') as f:
        json.dump(feature_index, f, indent=4)
        f.close()

    with open(os.path.join(output_path, 'features_descriptive.json'), 'w') as f:
        json.dump(feature_to_encoded, f, indent=4)
        f.close()

    with open(os.path.join(output_path, 'outcomes_variables.json'), 'w') as f:
        json.dump(encoded_outcomes, f, indent=4)
        f.close()


def run(console, build, articles=[], processed_folder='all', force=True):
    __console = console
    global print
    print = __console.print

    suffix = '_{}'.format(processed_folder)
    input_file = os.path.join(build, 'raw', 'cases_info', 'raw_cases_info{}.json'.format(suffix))
    input_folder = os.path.join(build, 'structured')
    output_folder = os.path.join(build, 'datasets')
    input_folder_bow = os.path.join(input_folder, 'bow')

    print(Markdown("- **Step configuration**"))
    print(TAB + '> Step folder: {}'.format(output_folder))
    make_build_folder(console, output_folder, force, strict=False)

    # Get the list of cases s.t. we have a BoW and TF-IDF representation
    files = [os.path.join(input_folder, f) for f in listdir(input_folder_bow) if isfile(join(input_folder_bow, f)) if
             '_bow.txt' in f]
    id_list = [f.split('/')[-1].split('_')[0] for f in files]

    # Read the case info
    cases = []
    try:
        with open(input_file, 'r') as f:
            content = f.read()
            cases = json.loads(content)
    except Exception as e:
        print(e)
        exit(1)

    # Filter the cases info to keep only the items in id_list
    cases = [c for c in cases if c['itemid'] in id_list]
    conclusion_key = 'conclusion' if processed_folder != 'multiclass' else 'mc_conclusion'
    cases = [c for c in cases if conclusion_key in c]

    keys = [
        "itemid",
        "respondent",
        "rank",
        "applicability",
        "decisiondate",
        "doctypebranch",
        "importance",
        "introductiondate",
        "judgementdate",
        "originatingbody_type",
        "originatingbody_name",
        "respondent",
        "respondentOrderEng",
        "separateopinion",
        "typedescription"

    ]

    keys_list = ["article", "documentcollectionid", "externalsources", "extractedappno", "kpthesaurus", "parties",
                 "scl", "representedby"]

    feature_index = {k: i for i, k in enumerate(keys + keys_list)}
    feature_to_value = dict(zip(keys + keys_list, [None] * (len(keys) + len(keys_list))))
    for c in cases:
        for k, v in c.items():
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
    for k, s in feature_to_value.items():
        for v in s:
            if k in keys:
                feature_to_encoded[u'{}={}'.format(k, v)] = count
            elif k in keys_list:
                feature_to_encoded[u'{}_has_{}'.format(k, v)] = count
            count += 1

    # Encode conclusions
    outcomes = {}
    for i, c in enumerate(cases):
        ccl = c[conclusion_key]
        for e in ccl:
            if e['type'] in ['violation', 'no-violation']:
                if e['article'] not in outcomes:
                    outcomes[e['article']] = {
                        'violation': 0,
                        'no-violation': 0,
                        'total': 0
                    }
                # if e['article'] == '8' and e['type'] == 'no-violation':
                #    print(c['docname'])
                outcomes[e['article']][e['type']] += 1
                outcomes[e['article']]['total'] += 1
        # Determine output
    encoded_outcomes = {}
    count = 1
    for i, o in outcomes.items():
        encoded_outcomes[i] = count
        count += 1

    offset = len(feature_to_encoded)

    print(Markdown('- **Generate dataset**'))
    generate_dataset(
        cases=cases,
        keys=keys,
        keys_list=keys_list,
        encoded_outcomes=encoded_outcomes,
        feature_index=feature_index,
        feature_to_encoded=feature_to_encoded,
        output_path=output_folder,
        name=processed_folder,
        offset=offset,
        processed_folder=input_folder,
        filter_classes=None if articles == [] else articles,
        force=force)

    shutil.make_archive(output_folder, 'zip', output_folder)


def main(args):
    console = Console(record=True)
    run(console,
        build=args.build,
        articles=args.articles,
        processed_folder=args.processed_folder,
        force=args.f)

def parse_args(parser):
    args = parser.parse_args()

    # Check path
    return args


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate final dataset files')
    parser.add_argument('--build', type=str, default="./build/echr_database/")
    parser.add_argument('--processed_folder', type=str, default="all")
    parser.add_argument('--name', type=str, default='multilabel')
    parser.add_argument('--articles', action='append', default=[])
    parser.add_argument('-f', action='store_true')
    args = parse_args(parser)

    main(args)
