#!/bin/python3
import subprocess
import argparse
import json
import os
from os import listdir
from os.path import isfile, join
import shutil
import sys
import time

LATEST_VERSION = '2.0.0'

MAX_DOCUMENTS = {
    '1.0.0': 144579,
    '2.0.0': 164767
}

MAX_DOCUMENTS['latest'] = MAX_DOCUMENTS[LATEST_VERSION]

STEPS = [
    ['get_cases_info.py'],
    ['filter_cases.py'],
    ['get_documents.py'],
    ['preprocess_documents.py'],
    ['normalize_documents.py'],
]
PROCESSING_STEP = True
DATASET_GEN_STEP = True
LIMIT_TOKENS = 10000

CASE_INFO_FOLDER = 'cases_info'

def call_and_print(cmd):
    p = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE)
    while True:
        out = p.stderr.read(1)
        if out == b'' and p.poll() != None:
            break
        if out != b'':
            sys.stdout.write(out.decode('utf-8'))
            sys.stdout.flush()

def main(args):

    if args.version is None:
        print('No version specified, the number of documents to retrieve will be automatically determined.')
    else:
        if args.version in MAX_DOCUMENTS:
            print('Version {} will be built with a maximum number of {} documents'.format(
                args.version, MAX_DOCUMENTS[args.version]))
            if STEPS:
                STEPS[0].extend(['--max_documents', MAX_DOCUMENTS[args.version]])
        else:
            print('Version "{}" is incorrect. Supported versions are: {}.'.format(
                args.version, ', '.join(MAX_DOCUMENTS.keys())))

    start_time = time.time()

    flags = ['-f'] if args.force else []
    flags.extend(['--build', args.build])

    for step in STEPS:
        cmd = ['python3'] + step + flags
        cmd = ' '.join(map(str, cmd))
        call_and_print(cmd)


    path = os.path.join(args.build, CASE_INFO_FOLDER)
    files = [f for f in listdir(path) if isfile(join(path, f))]
    files = [f for f in files if f.startswith('raw_cases_info')]
    datasets = [f.split('.')[0][len('raw_cases_info_'):] for f in files]
    datasets = [f for f in datasets if f]
    if PROCESSING_STEP:
        base_cmd = ['python3', 'process_documents.py', '--processed_folder']
        for d in datasets:
            print('# Processing documents for dataset {}'.format(d))
            flags_process = flags + ['--limit_tokens', LIMIT_TOKENS]
            cmd = base_cmd + [d] + flags_process
            cmd = ' '.join(map(str, cmd))
            call_and_print(cmd)

    if DATASET_GEN_STEP:
        base_cmd = ['python3', 'generate_datasets.py', '--processed_folder']
        for d in datasets:
            print('# Generate dataset {}'.format(d))
            flags_gen = []
            nart = None
            if d not in ['multiclass', 'multilabel']:
                if '_' in d:
                    nart = d.split('_')[-1]
                if nart:
                    flags_gen.extend(['--articles', nart])
            cmd = []
            cmd.extend(base_cmd + [d] + flags + flags_gen)
            cmd = ' '.join(map(str, cmd))
            call_and_print(cmd)

    print("# Database and datasets generated in {}s".format(time.time() - start_time))
    print("# Prepare release folder structure")
    paths = ['unstructured', 'structured', 'raw']
    for p in paths:
        try:
            os.mkdir(os.path.join(args.build, p))
        except Exception:
            pass


    cases_files = [f for f in listdir(os.path.join(args.build, 'preprocessed_documents'))
                   if isfile(os.path.join(args.build, 'preprocessed_documents', f)) and '.json' in f]
    cases = []
    for f in cases_files:
        with open(os.path.join(args.build, 'preprocessed_documents', f)) as json_file:
            data = json.load(json_file)
            cases.append(data)

    # Unstructured
    with open(os.path.join(args.build, 'unstructured', 'cases.json'), 'w') as outfile:
        json.dump(cases, outfile, indent=4)

    # Structured
    from normalize_database import format_structured_json, COL_HINT
    flat_cases , representatives, extractedapp, scl, decision_body = format_structured_json(cases)
    schema_hints = {
        'article': {
            'col_type': COL_HINT.HOT_ONE
        },
        'documentcollectionid': {
            'col_type': COL_HINT.HOT_ONE
        },
        'applicability': {
            'col_type': COL_HINT.HOT_ONE
        },
        'paragraphs': {
            'col_type': COL_HINT.HOT_ONE
        },
        'conclusion': {
            'col_type': COL_HINT.HOT_ONE,
            'sub_element': 'flatten'
        }
    }

    output_path = os.path.join(args.build, 'structured')
    with open(os.path.join(output_path, 'flat_cases.json'), 'w') as outfile:
        json.dump(flat_cases, outfile, indent=4)

    with open(os.path.join(output_path, 'schema_hint.json'), 'w') as outfile:
        json.dump(schema_hints, outfile, indent=4)

    cmd = ['python3'] + ['normalize_database.py'] + flags + \
          ['--database_json', os.path.join(output_path, 'flat_cases.json'),
           '--schema_hints', os.path.join(output_path, 'schema_hint.json'),
           '--output_prefix', 'cases',
           '--build', output_path
    ]
    cmd = ' '.join(map(str, cmd))
    call_and_print(cmd)
    os.remove(os.path.join(output_path, 'flat_cases.json'))
    os.remove(os.path.join(output_path, 'cases_flat_schema.json'))
    os.remove(os.path.join(output_path, 'cases_flat_type_mapping.json'))
    shutil.copy(os.path.join(args.build, 'datasets_documents', 'all', 'features_text.json'), os.path.join(output_path))
    shutil.copy(os.path.join(args.build, 'datasets_documents', 'all', 'statistics_datasets.json'), os.path.join(output_path))

    print('Generate appnos matrice')
    matrice_appnos = {}
    for k, v in extractedapp.items():
        matrice_appnos[k] = {e:1 for e in v['appnos']}
    with open(os.path.join(output_path, 'matrice_appnos.json'), 'w') as outfile:
        json.dump(matrice_appnos, outfile, indent=4)

    print('Generate scl matrice')
    matrice_scl = {}
    for k, v in scl.items():
        matrice_scl[k] = {e: 1 for e in v['scl']}
    with open(os.path.join(output_path, 'matrice_scl.json'), 'w') as outfile:
        json.dump(matrice_scl, outfile, indent=4)

    print('Generate representatives matrice')
    matrice_representedby = {}
    for k, v in representatives.items():
        matrice_representedby[k] = {e: 1 for e in v['representedby']}
    with open(os.path.join(output_path, 'matrice_representatives.json'), 'w') as outfile:
        json.dump(matrice_representedby, outfile, indent=4)

    print('Generate decision body matrice')
    matrice_decision_body = {}
    for k, v in decision_body.items():
        matrice_decision_body[k] = {k:v for k,v in v['role'].items()}
    with open(os.path.join(output_path, 'matrice_decision_body.json'), 'w') as outfile:
        json.dump(matrice_decision_body, outfile, indent=4)

    processed_folder = os.path.join(args.build, 'processed_documents', 'all')
    try:
        os.mkdir(os.path.join(args.build, 'structured', 'tfidf'))
    except Exception:
        pass
    tfidf_files = [f for f in listdir(processed_folder)
                   if isfile(os.path.join(processed_folder, f)) and 'tfidf.txt' in f]

    for f in tfidf_files:
        shutil.copy(os.path.join(processed_folder, f), os.path.join(args.build, 'structured', 'tfidf', f))

    try:
        os.mkdir(os.path.join(args.build, 'structured', 'bow'))
    except Exception:
        pass
    bow_files = [f for f in listdir(processed_folder)
                 if isfile(os.path.join(processed_folder, f)) and 'bow.txt' in f]

    for f in bow_files:
        shutil.copy(os.path.join(processed_folder, f), os.path.join(args.build, 'structured', 'bow', f))

    # Raw
    shutil.make_archive(os.path.join(args.build, 'raw', 'judgments'), 'zip',
                        os.path.join(args.build, 'raw_documents'))
    shutil.make_archive(os.path.join(args.build, 'raw', 'normalized'), 'zip',
                        os.path.join(args.build, 'raw_normalized_documents'))

    # All
    from zipfile import ZipFile
    with ZipFile(os.path.join(args.build, 'all.zip'), 'w') as zipObj:
        # Iterate over all the files in directory
        folders = ['unstructured', 'raw', 'structured']
        for f in folders:
            for folderName, subfolders, filenames in os.walk(os.path.join(args.build, f)):
                for filename in filenames:
                    if not filename.endswith('.zip'):
                        filePath = os.path.join(folderName, filename)
                        zipObj.write(filePath)

    shutil.make_archive(os.path.join(args.build, 'structured', 'tfidf'), 'zip',
                        os.path.join(args.build, 'structured', 'tfidf'))
    shutil.make_archive(os.path.join(args.build, 'structured', 'bow'), 'zip',
                        os.path.join(args.build, 'structured', 'bow'))

def parse_args(parser):
    args = parser.parse_args()

    # Check path
    return args

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description='Generate the whole database')
    parser.add_argument('--build', type=str, default="./build/echr_database/")
    parser.add_argument('-f', '--force', action='store_true')
    parser.add_argument('--version', type=str, help='Version to build among: {}'.format(
        ', '.join(MAX_DOCUMENTS.keys())))
    args = parse_args(parser)

    main(args)
