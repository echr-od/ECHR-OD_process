#!/bin/python3
import argparse
import requests
import json
import os
import shutil

base_url = "http://hudoc.echr.coe.int/app/conversion/docx/?library=ECHR&filename=please_give_me_the_document.docx&id="
perma_url = "http://hudoc.echr.coe.int/eng?i="

def get_documents(id_list, folder, update):
    for i, doc_id in enumerate(id_list):
        print("Document {}/{}: {}".format(i, len(id_list), doc_id))
        filename = "%s.docx"%(doc_id.strip())
        filename = os.path.join(folder, filename)
        if update and not os.path.isfile(filename):
            url = base_url + doc_id.strip()
            r = requests.get(url, stream=True)
            if not r.ok:
                print("Failed to fetch document %s"%(doc_id))
                print("URL: %s"%(url))
                print("Permalink: %s"%(perma_url + doc_id.strip()))
                continue
            with open(filename, 'wb') as f:
                for block in r.iter_content(1024):
                    f.write(block)
            print("request complete, see %s"%(filename))
        else:
            print("skip as document exists already")

def main(args):
    id_list = []
    try:
        with open(args.input_file, 'r') as f:
            content = f.read()
            cases = json.loads(content)
            id_list = [i['itemid'] for i in cases]
    except Exception as e:
        print(e)
        exit(1)

    if not args.u:
        try:
            if args.f:
                shutil.rmtree(args.output_folder)
            os.mkdir(args.output_folder)
        except Exception as e:
            print(e)
            exit(1)

    get_documents(id_list, args.output_folder, args.u)

def parse_args(parser):
    args = parser.parse_args()

    # Check path
    return args

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Filter and format ECHR cases information')
    parser.add_argument('--input_file', type=str, default="./cases_info/raw_cases_info.json")
    parser.add_argument('--output_folder', type=str, default="./raw_documents")
    parser.add_argument('-f', action='store_true')
    parser.add_argument('-u', action='store_true')
    args = parse_args(parser)

    main(args)
 