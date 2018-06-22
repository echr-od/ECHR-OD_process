#!/bin/python3
import subprocess
import argparse
import os
from os import listdir
from os.path import isfile, join
import shutil
import sys
from time import sleep

STEPS = [
    #['get_cases_info.py'],
    #['filter_cases.py'],
    #['get_documents.py'],
    #['preprocess_documents.py'],
    #['normalize_documents.py'],
]

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
    try:
        if args.f:
            shutil.rmtree(args.build)
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
    
    for d in datasets:
        print('# Processing documents for dataset {}'.format(d))
        cmd = ['python', 'process_documents.py', '--processed_folder', d] + flags
        cmd = ' '.join(cmd)
        call_and_print(cmd)

    for d in datasets:
        print('# Generate dataset {}'.format(d))
        cmd = ['python', 'generate_datasets.py', '--processed_folder', d] + flags
        cmd = ' '.join(cmd)
        call_and_print(cmd)

def parse_args(parser):
    args = parser.parse_args()

    # Check path
    return args

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description='Generate the whole database')
    parser.add_argument('--build', type=str, default="./build/echr_database/")
    parser.add_argument('-f', action='store_true')
    args = parse_args(parser)

    main(args)