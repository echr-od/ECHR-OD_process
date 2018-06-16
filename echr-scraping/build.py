#!/bin/python3
import subprocess
import argparse
import os
import shutil
from time import sleep

STEPS = [
    #['get_cases_info.py'],
    ['filter_cases.py'],
    #['get_documents.py'],
    #['preprocess_documents.py'],
    #['generate_dictionary.py'],
    #['process_documents.py'],
    ['generate_datasets.py']
]


def main(args):
    try:
        if args.f:
            shutil.rmtree(args.base_folder)
        os.mkdir(args.base_folder)
    except Exception as e:
        print(e)
        exit(1)


    flags = ['-f'] if args.f else []

    for step in STEPS:
        cmd = ['python'] + step + flags
        print(cmd)
        output = subprocess.check_output(cmd)
        
def parse_args(parser):
    args = parser.parse_args()

    # Check path
    return args

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description='Generate the whole database')
    parser.add_argument('--base_folder', type=str, default="./build")
    parser.add_argument('-f', action='store_true')
    args = parse_args(parser)

    main(args)