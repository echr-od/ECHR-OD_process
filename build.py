#!/bin/python3
import subprocess
import argparse
import os
from os import listdir
from os.path import isfile, join
import shutil
import sys
import time


MAX_DOCUMENTS = {
    '1.0.0': 144579
}

STEPS = [
    ['get_cases_info.py', '--max_documents', MAX_DOCUMENTS['1.0.0']],
    ['filter_cases.py'],
    ['get_documents.py'],
    ['preprocess_documents.py'],
    ['normalize_documents.py'],
]
PROCESSING_STEP = False
DATASET_GEN_STEP = True
LIMIT_TOKENS = 5000

CASE_INFO_FOLDER = 'cases_info'

def call_and_print(cmd):
    p = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE)
    while True:
        out = p.stderr.read(1)
        if out == '' and p.poll() != None:
            break
        if out != '':
            sys.stdout.write(out)
            sys.stdout.flush()

def main(args):
    start_time = time.time()
    try:
        #if args.f:
        #    shutil.rmtree(args.build)
        os.mkdir(args.build)
    except Exception as e:
        print(e)
        #exit(1)

    flags = ['-f'] if args.f else []
    flags.extend(['--build', args.build])

    for step in STEPS:
        cmd = ['python'] + step + flags
        cmd = ' '.join(cmd)
        call_and_print(cmd)

    
    path = os.path.join(args.build, CASE_INFO_FOLDER)
    files = [f for f in listdir(path) if isfile(join(path, f))]
    files = [f for f in files if f.startswith('raw_cases_info')]
    datasets = [f.split('.')[0][len('raw_cases_info_'):] for f in files]
    datasets = [f for f in datasets if f]
    
    if PROCESSING_STEP:
        base_cmd = ['python', 'process_documents.py', '--processed_folder']
        for d in datasets:
            print('# Processing documents for dataset {}'.format(d))
            flags_process = flags + ['--limit_tokens', LIMIT_TOKENS]
            cmd = base_cmd + [d] + flags_process
            cmd = ' '.join(cmd)
            call_and_print(cmd)

    if DATASET_GEN_STEP:
        base_cmd = ['python', 'generate_datasets.py', '--processed_folder']
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
            cmd = ' '.join(cmd)
            call_and_print(cmd)

    print("# Database and datasets generated in {}s".format(time.time() - start_time))

def parse_args(parser):
    args = parser.parse_args()

    # Check path
    return args

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description='Generate the whole database')
    parser.add_argument('--build', type=str, default="./build/echr_database/")
    parser.add_argument('-f', action='store_true')
    parser.add_argument('--version', action='store_true')
    args = parse_args(parser)

    main(args)
