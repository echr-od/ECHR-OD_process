#!/bin/python3
import argparse
import requests
import json
import os
import shutil
from time import sleep

fields = [
    "sharepointid", 
    "Rank", 
    "itemid", 
    "docname", 
    "doctype", 
    "application", 
    "appno", 
    "conclusion", 
    "importance", 
    "originatingbody", 
    "typedescription", 
    "kpdate", 
    "kpdateAsText", 
    "documentcollectionid", 
    "documentcollectionid2", 
    "languageisocode", 
    "extractedappno", 
    "isplaceholder", 
    "doctypebranch", 
    "respondent", 
    "respondentOrderEng", 
    "ecli", 
    "article", 
    "applicability", 
    "decisiondate", 
    "externalsources", 
    "introductiondate", 
    "issue", 
    "judgementdate", 
    "kpthesaurus", 
    "meetingnumber", 
    "representedby", 
    "separateopinion", 
    "scl"
]
base_url = "http://hudoc.echr.coe.int/app/query/results?query=((((((((((((((((((((%20contentsitename%3AECHR%20AND%20(NOT%20(doctype%3DPR%20OR%20doctype%3DHFCOMOLD%20OR%20doctype%3DHECOMOLD)))%20XRANK(cb%3D14)%20doctypebranch%3AGRANDCHAMBER)%20XRANK(cb%3D13)%20doctypebranch%3ADECGRANDCHAMBER)%20XRANK(cb%3D12)%20doctypebranch%3ACHAMBER)%20XRANK(cb%3D11)%20doctypebranch%3AADMISSIBILITY)%20XRANK(cb%3D10)%20doctypebranch%3ACOMMITTEE)%20XRANK(cb%3D9)%20doctypebranch%3AADMISSIBILITYCOM)%20XRANK(cb%3D8)%20doctypebranch%3ADECCOMMISSION)%20XRANK(cb%3D7)%20doctypebranch%3ACOMMUNICATEDCASES)%20XRANK(cb%3D6)%20doctypebranch%3ACLIN)%20XRANK(cb%3D5)%20doctypebranch%3AADVISORYOPINIONS)%20XRANK(cb%3D4)%20doctypebranch%3AREPORTS)%20XRANK(cb%3D3)%20doctypebranch%3AEXECUTION)%20XRANK(cb%3D2)%20doctypebranch%3AMERITS)%20XRANK(cb%3D1)%20doctypebranch%3ASCREENINGPANEL)%20XRANK(cb%3D4)%20importance%3A1)%20XRANK(cb%3D3)%20importance%3A2)%20XRANK(cb%3D2)%20importance%3A3)%20XRANK(cb%3D1)%20importance%3A4)%20XRANK(cb%3D2)%20languageisocode%3AENG)%20XRANK(cb%3D1)%20languageisocode%3AFRE&select={}&sort=&rankingModelId=4180000c-8692-45ca-ad63-74bc4163871b".format(','.join(fields))
length = 500 #maximum number of items per request

def get_case_info(base_url, max_documents, path):
    for start in range(0, max_documents, length):
        print("Fetching and writing %d.json"%(start))
        with open(os.path.join(path, "%d.json"%(start)), 'wb') as f:
            url = base_url + "&start=%d&length=%d"%(start, length)
            r = requests.get(url, stream=True)
            if not r.ok:
                print("Failed to fetch %d to %d"%(start, length))
                continue
            for block in r.iter_content(1024):
                f.write(block)

def main(args):
    try:
        if args.f:
            shutil.rmtree(args.folder)
        os.mkdir(args.folder)
    except Exception as e:
        print(e)
        exit(1)
            
    get_case_info(base_url, args.max_documents, args.folder)

def parse_args(parser):
    args = parser.parse_args()

    # Check path
    return args

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description='Retrieve ECHR cases information')
    parser.add_argument('--folder', type=str, default="./raw_cases_info")
    parser.add_argument('--max_documents', type=int, default=144579)
    parser.add_argument('-f', action='store_true')
    args = parse_args(parser)

    main(args)
 