import argparse
import requests
import json
import os
from time import sleep
from os import listdir
from os.path import isfile, join
import re
from collections import Counter

def format_parties(parties):
    #"CASE OF AXEL SPRINGER AG v. GERMANY (No. 2)"
    if parties.startswith('CASE OF '):
        parties = parties[len('CASE OF '):]
    if parties[-1] == ')':
        parties = parties.split('(')[0]
    parties = parties.split(' v. ')
    parties = [p.strip() for p in parties]
    return parties

def format_conclusion(ccl):
    final_ccl = []
    chunks = [c for c in ccl.split(')') if len(c)]
    art = []
    for c in chunks:
        if '(' not in c:
            art.extend(c.split(';'))
        else:
            art.append(c)
    art = [a for a in art if len(a) > 0]
    # print(art)
    for c in art:
        #print(c)
        a = c.split('(')
        b = a[1].split(';') if len(a) > 1 else None
        #print('MENTION ', b)
        articles = [d.strip() for d in a[0].split(';')]
        articles = [d for d in articles if len(d) > 0]
        #print('ART ', articles)
        if not len(articles):
            if b:
                if 'mentions' in final_ccl[-1]:
                    final_ccl[-1]['mentions'].extend(b)
                else:
                    final_ccl[-1]['mentions'] = b
            continue
        article = articles[-1] if not articles[-1].startswith(';') else articles[-1][1:]
        conclusion = {'element': article }
        if b:
            conclusion['details'] = b
        if len(article.strip()) == 0:
            if b is not None:
                final_ccl[-1]['mentions'] = b
        else:
            final_ccl.append(conclusion)
    if len(articles) > 1:
        for a in articles[:-1]:
            if len(a) > 0:
                final_ccl.append({'element': a})

    #'''
    to_append = []
    for i, e in enumerate(final_ccl):
        l =  re.sub(' +', ' ', e['element'].lower().strip())
        t = 'other'
        if l.startswith('violation'):
            t = 'violation'
        elif l.startswith('no-violation') or l.startswith('no violation'):
            t = 'no-violation'
        final_ccl[i]['type'] = t
        if t != 'other':
            art = None
            if ' and ' in l:
                l = l.replace(' and ', '+')
            if 'violations of p1-1' in l or 'violation of p1-1' in l:
                final_ccl[i]['article'] = 'p1'
            elif 'violations of p1-3' in l or 'violation of p1-2' in l:
                final_ccl[i]['article'] = 'p1'
            elif 'violations of p1-3' in l or 'violation of p1-3' in l:
                final_ccl[i]['article'] = 'p1'
            elif 'violations of p4-2' in l or 'violation of p4-2' in l:
                final_ccl[i]['article'] = 'p4'
            elif 'violations of p4-4' in l or 'violation of p4-4' in l:
                final_ccl[i]['article'] = 'p4'
            elif 'violations of p7-4' in l or 'violation of p7-4' in l:
                final_ccl[i]['article'] = 'p7'
            elif 'violations of p7-1' in l or 'violation of p7-1' in l:
                final_ccl[i]['article'] = 'p7'
            elif 'violations of p7-2' in l or 'violation of p7-2' in l:
                final_ccl[i]['article'] = 'p7'
            elif 'violations of p12-1' in l or 'violation of p12-1' in l:
                final_ccl[i]['article'] = 'p12'
            elif 'violations of p6-3-c' in l or 'violation of p6-3-c' in l:
                final_ccl[i]['article'] = 'p6'
            elif 'violations of p7-5' in l or 'violation of p7-5' in l:
                final_ccl[i]['article'] = 'p7'
            elif 'violations of 6-1' in l or 'violation of 6-1' in l:
                final_ccl[i]['article'] = '6'
            else:
                b = l.split()
                #print(b)
                for j, a in enumerate(b):
                    if a.startswith('art'):
                        if a.lower().startswith('art.') and not a.lower().startswith('art. ') and len(a) > 4:
                            art = a.lower()[4:]
                        else:
                            art = b[j+1]
                        break
                if art is not None:
                    art = art.split('+')
                    final_ccl[i]['article'] = art[0].split('-')[0]
                    #'''
                    if len(art) > 1:
                        for m in art[1:]:
                            item = final_ccl[i]
                            item['article'] = m.split('-')[0]
                            to_append.append(item)
                #'''
    #'''
    final_ccl.extend(to_append)
    return final_ccl

def format_article(article):
    res = []
    for a in article.split(';'):
        res.extend(a.split('+'))
    res = list(set(map(unicode.strip, res)))
    return res

def filter_cases(cases):
    cases = [i for i in cases if i["languageisocode"] == "ENG"]
    cases = [i for i in cases if "No-violation" in i["conclusion"] or "No violation" in i["conclusion"] or "Violation" in i["conclusion"] or "violation" in i["conclusion"]]
    #print('LEN: {}'.format(len(res)))
    cases = [i for i in cases if i["application"].startswith("MS WORD")]
    cases = [i for i in cases if i["doctype"] == "HEJUD"]
    #print('LEN: {}'.format(len(res)))
    cases = [i for i in cases if i['itemid'] not in ["001-154354", "001-108395", "001-79411"]]

    return cases

def format_cases(cases):
    for i, c in enumerate(cases):
        print('Format case {}/{}'.format(i, len(cases)))
        cases[i]['parties'] = format_parties(cases[i]['docname'])
        #print(cases[i]['conclusion'])
        cases[i]['conclusion_'] = format_conclusion(c['conclusion'])
        cases[i]['articles_'] = cases[i]['article']
        cases[i]['article'] = format_article(c['article'])
        
        cases[i]['externalsources'] = cases[i]["externalsources"].split(';') if len(cases[i]['externalsources']) > 0 else []
        cases[i]["documentcollectionid"] = cases[i]["documentcollectionid"].split(';') if len(cases[i]['documentcollectionid']) > 0 else []
        cases[i]["issue"] = cases[i]["issue"].split(';') if len(cases[i]['issue']) > 0 else []
        cases[i]["representedby"] = cases[i]["representedby"].split(';') if len(cases[i]['representedby']) > 0 else []
        cases[i]["extractedappno"] = cases[i]["extractedappno"].split(';')

        cases[i]['externalsources'] = [e.strip() for e in cases[i]['externalsources']]
        cases[i]['documentcollectionid'] = [e.strip() for e in cases[i]['documentcollectionid']]
        cases[i]['issue'] = [e.strip() for e in cases[i]['issue']]
        cases[i]['representedby'] = [e.strip() for e in cases[i]['representedby']]
        cases[i]['extractedappno'] = [e.strip() for e in cases[i]['extractedappno']]


        del cases[i]["isplaceholder"]
        cases[i]["kpdate"] = cases[i]['kpdateAsText']
        del cases[i]['kpdateAsText']
        del cases[i]["documentcollectionid2"]
        cases[i]["kpthesaurus"] = cases[i]["kpthesaurus"].split(';')
        cases[i]["scl"] = cases[i]["scl"].split(';') if cases[i]["scl"].strip() else []
        del cases[i]["application"]
        del cases[i]["doctype"]
        del cases[i]["meetingnumber"]
        #print(c['columns']['itemid'], c['columns'])
    return cases

def generate_statistics(cases):
    def generate_count(k, cases):
        s = []
        for c in cases:
            if k == 'conclusion_':
                # We do not take into account mention and details
                s.extend([a['element'] for a in c[k]])
            else:
                if type(c[k]) == list:
                    if len(c[k]):
                        s.extend(c[k])
                else: #string
                    if len(c[k].strip()):
                        s.append(c[k])
        return s

    keys = cases[0].keys()
    except_k = []
    for k in [i for i in keys if i not in except_k]:
        s = generate_count(k, cases)
        #print(s)
        s = Counter(s)
        print('Attribute "{}": \n - Cardinal: {}\n - Density: {}'.format(k, len(s), float(len(s)) / len(cases)))
        if k == "doctypebranch":
            print(s)
    '''
    # Statistiques
    s = []
    for c in cases:
        if len(c["article"]):
            s.extend(c["article"])
    print(len(s), len(cases))
    print(Counter(s))

    s = []
    for c in cases:
        s.append(c["Rank"])
    #print(Counter(s))
    '''
    


def main(args):
    cases = []
    files = [os.path.join(args.input_folder, f) for f in listdir(args.input_folder) if isfile(join(args.input_folder, f)) if '.json' in f]
    for p in files:
        try:
            with open(p, 'r') as f:
                content = f.read()
                index = json.loads(content)
                cases.extend(index["results"])
        except Exception as e:
            print(p, e)
    cases = [c["columns"] for c in cases]

    cases = filter_cases(cases)
    cases = format_cases(cases)

    generate_statistics(cases)

    with open(os.path.join(args.output_folder, 'raw_cases_info.json'), 'w') as outfile:
        json.dump(cases, outfile, indent=4, sort_keys=True)


def parse_args(parser):
    args = parser.parse_args()

    # Check path
    return args

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Filter and format ECHR cases information')
    parser.add_argument('--input_folder', type=str, default="./raw_cases_info")
    parser.add_argument('--output_folder', type=str, default="./")
    parser.add_argument('-f', action='store_true')
    args = parse_args(parser)

    main(args)
 