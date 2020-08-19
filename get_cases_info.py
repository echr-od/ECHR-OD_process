#!/usr/bin/python
import argparse
import requests
import os
import shutil
from selenium import webdriver
from time import sleep
import urllib3

urllib3.util.ssl_.DEFAULT_CIPHERS = 'ALL:@SECLEVEL=1'
MAX_RETRY = 5

# Fields to retrieve
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
BASE_URL = "http://hudoc.echr.coe.int/app/query/results?query=((((((((((((((((((((%20contentsitename%3AECHR%20AND%20(NOT%20(doctype%3DPR%20OR%20doctype%3DHFCOMOLD%20OR%20doctype%3DHECOMOLD)))%20XRANK(cb%3D14)%20doctypebranch%3AGRANDCHAMBER)%20XRANK(cb%3D13)%20doctypebranch%3ADECGRANDCHAMBER)%20XRANK(cb%3D12)%20doctypebranch%3ACHAMBER)%20XRANK(cb%3D11)%20doctypebranch%3AADMISSIBILITY)%20XRANK(cb%3D10)%20doctypebranch%3ACOMMITTEE)%20XRANK(cb%3D9)%20doctypebranch%3AADMISSIBILITYCOM)%20XRANK(cb%3D8)%20doctypebranch%3ADECCOMMISSION)%20XRANK(cb%3D7)%20doctypebranch%3ACOMMUNICATEDCASES)%20XRANK(cb%3D6)%20doctypebranch%3ACLIN)%20XRANK(cb%3D5)%20doctypebranch%3AADVISORYOPINIONS)%20XRANK(cb%3D4)%20doctypebranch%3AREPORTS)%20XRANK(cb%3D3)%20doctypebranch%3AEXECUTION)%20XRANK(cb%3D2)%20doctypebranch%3AMERITS)%20XRANK(cb%3D1)%20doctypebranch%3ASCREENINGPANEL)%20XRANK(cb%3D4)%20importance%3A1)%20XRANK(cb%3D3)%20importance%3A2)%20XRANK(cb%3D2)%20importance%3A3)%20XRANK(cb%3D1)%20importance%3A4)%20XRANK(cb%3D2)%20languageisocode%3AENG)%20XRANK(cb%3D1)%20languageisocode%3AFRE&select={}&sort=&rankingModelId=4180000c-8692-45ca-ad63-74bc4163871b".format(','.join(fields))
length = 500 #maximum number of items per request

def determine_max_documents(default_value):
    """Automatically determine the number of available documents in HUDOC

        :param default_value: fallback value
        :type default_value: [int]
    """
    drivers = ['PhantomJS', 'Chrome', 'Firefox']
    browser = None
    for driver in drivers:
        try:
            get_driver = getattr(webdriver, driver)
            browser = get_driver()
            break
        except Exception as e:
            print('Could not find {} webdriver. See doc#webdrivers'.format(driver))
    max_documents = None
    if browser is not None:
        url = "https://hudoc.echr.coe.int/eng#%20"
        browser.implicitly_wait(30)
        browser.get(url)
        for i in range(0,5):
            result = browser.find_element_by_class_name('resultNumber')
            if int(result.text) > 0:
                max_documents = int(result.text)
                break
            else:
                sleep(1)
    if max_documents is None:
        if browser is None:
            print('Could not find any webdriver - fallback using default value')
        max_documents = default_value
    return max_documents


def get_case_info(base_url, max_documents, path):
    """Get case information from HUDOC

        :param base_url: base url to query for documents
        :type base_url: string
        :param: max_documents: maximal number of documents to retrieve
        :type: int
        :param: path: path to store the information
        :type: str
    """
    for start in range(0, max_documents, length):
        print(" - Fetching information from cases {} to {}.".format(start, start+length))
        with open(os.path.join(path, "%d.json"%(start)), 'wb') as f:
            url = base_url + "&start=%d&length=%d"%(start, length)
            for i in range(MAX_RETRY):
                try:
                    r = requests.get(url, stream=True)
                    if not r.ok:
                        print('\t({}/{}) Failed to fetch information {} to {}'.format(
                            i + 1, MAX_RETRY, start, start + length))
                        continue
                    for block in r.iter_content(1024):
                        f.write(block)
                    break
                except Exception as e:
                    print('\t({}/{}) Failed to fetch information {} to {}'.format(
                        i + 1, MAX_RETRY, start, start + length))

def main(args):
    raw_case_folder = os.path.join(args.build, 'raw_cases_info')
    try:
        if args.f:
            shutil.rmtree(raw_case_folder)
        os.mkdir(raw_case_folder)
    except Exception as e:
        print(e)
        exit(1)

    max_documents = args.max_documents
    if max_documents == -1:
        print('Determining the number of documents to retrieve...')
        max_documents = determine_max_documents(144579)  # v1.0.0 value
    
    print('# Get case information from HUDOC')
    print('- Max documents: {}'.format(max_documents))
    get_case_info(BASE_URL, max_documents, raw_case_folder)

def parse_args(parser):
    args = parser.parse_args()

    # Check path
    return args

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description='Retrieve ECHR cases information')
    parser.add_argument('--build', type=str, default="./build/echr_database/")
    parser.add_argument('--max_documents', type=int, default=-1)
    parser.add_argument('-f', action='store_true')
    args = parse_args(parser)

    main(args)
 