#!/usr/bin/python
import argparse
from collections import Counter
import json
from os import listdir, path, mkdir
import re
import shutil
import sys

def format_parties(parties):
    """Return the list of parties from the case title.

        :param parties: string containing the parties name
        :type parties: str
        :return: list of names
        :rtype: [str]
    """
    if parties.startswith('CASE OF '):
        parties = parties[len('CASE OF '):]
    if parties[-1] == ')':
        parties = parties.split('(')[0]
    parties = parties.split(' v. ')
    parties = [p.strip() for p in parties]
    return parties

def format_conclusion(ccl):
    """Format a conclusion string into a list of elements:

        :Example:

        ```json
            {
                "article": "3", 
                "details": [
                    "Article 3 - Degrading treatment", 
                    "Inhuman treatment"
                ], 
                "element": "Violation of Article 3 - Prohibition of torture", 
                "mentions": [
                    "Substantive aspect"
                ], 
                "type": "violation"
            }, 
            {
                "article": "13", 
                "details": [
                    "Article 13 - Effective remedy"
                ], 
                "element": "Violation of Article 13 - Right to an effective remedy", 
                "type": "violation"
            }
        ```
        :param ccl: conclusion string
        :type ccl: str
        :return: list of formatted conclusion element
        :rtype: [dict]
    """
    final_ccl = []
    chunks = [c for c in ccl.split(')') if len(c)]
    art = []
    for c in chunks:
        if '(' not in c:
            art.extend(c.split(';'))
        else:
            art.append(c)
    art = [a for a in art if len(a) > 0]
    for c in art:
        a = c.split('(')
        b = a[1].split(';') if len(a) > 1 else None
        articles = [d.strip() for d in a[0].split(';')]
        articles = [d for d in articles if len(d) > 0]
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
            if ' and art. ' in l:
                l = l.replace(' and art. ', '')
            if ' and of ' in l:
                l = l.replace(' and of ', '+')
            if ' and ' in l:
                l = l.replace(' and ', '+')
            # TODO: Remove this ugly code...
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

                for j, a in enumerate(b):
                    if a.startswith('art'):
                        if a.lower().startswith('art.') and not a.lower().startswith('art. ') and len(a) > 4:
                            art = a.lower()[4:]
                        else:
                            art = b[j+1]
                        break
                if art is not None:
                    art = art.split('+')
                    final_ccl[i]['article'] = art[0].split('-')[0].replace('.', '')
                    if len(art) > 1:
                        for m in art[1:]:
                            item = final_ccl[i]
                            item['article'] = m.split('-')[0]
                            to_append.append(item)

    final_ccl.extend(to_append)
    return final_ccl

def format_article(article):
    """Format the list of articles.

        :param article: string containing the list of articles
        :type article: str
        :return: list of articles
        :rtype: [str]
    """
    articles = article.split(';')
    articles = [a for sublist in articles for a in sublist.split('+')]
    articles = [a.split('-')[0].strip() for a in articles]
    return list(set(articles))

def format_subarticle(article):
    """Format the list of subarticles.

        :param article: string containing the list of articles
        :type article: str
        :return: list of subarticles
        :rtype: [str]
    """
    articles = article.split(';')
    articles = [a for sublist in articles for a in sublist.split('+')]
    res = list(set(articles))
    return res

def format_cases(cases):
    """
        Format the cases from raw information

        :param cases: list of cases raw information
        :type cases: [dict]
        :return: list of formatted cases
        :rtype: [dict]
    """
    COUNTRIES = {}
    with open('countries.json') as f:
        data = json.load(f)
        for c in data:
            COUNTRIES[c['alpha-3']] = {
                'alpha2': c['alpha-2'].lower(),
                'name': c['name']
            }

    ORIGINATING_BODY = {}
    with open('originatingbody.json') as f:
        ORIGINATING_BODY = json.load(f)
    for i, c in enumerate(cases):
        sys.stdout.write('\r - Format case {}/{}'.format(i+1, len(cases)))
        cases[i]['parties'] = format_parties(cases[i]['docname'])
        cases[i]['__conclusion'] = cases[i]['conclusion']
        cases[i]['conclusion'] = format_conclusion(c['__conclusion'])
        cases[i]['__articles'] = cases[i]['article']
        cases[i]['article'] = format_article(cases[i]['__articles'])
        cases[i]['paragraphs'] = format_subarticle(cases[i]['__articles'])
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

        cases[i]['country'] = COUNTRIES[cases[i]['respondent'].split(';')[0]]
        cases[i]['originatingbody_type'] = ORIGINATING_BODY[cases[i]['originatingbody']]['type']
        cases[i]['originatingbody_name'] = ORIGINATING_BODY[cases[i]['originatingbody']]['name']

        cases[i]["rank"] = cases[i]['Rank']
        del cases[i]["Rank"]

        del cases[i]["isplaceholder"]
        cases[i]["kpdate"] = cases[i]['kpdateAsText']
        del cases[i]['kpdateAsText']
        del cases[i]["documentcollectionid2"]
        cases[i]["kpthesaurus"] = cases[i]["kpthesaurus"].split(';')
        cases[i]["scl"] = cases[i]["scl"].split(';') if cases[i]["scl"].strip() else []
        del cases[i]["application"]
        del cases[i]["doctype"]
        del cases[i]["meetingnumber"]
    print('')
    return cases


def filter_cases(cases):
    """Filter the list of cases.

        :param cases: list of cases
        :type cases: [dict]
        :return: filtered list of cases
        :rtype: [dict]
    """
    total = len(cases)
    print(' - Total number of cases before filtering: {}'.format(total))
    print(' - Remove non-english cases')
    cases = [i for i in cases if i["languageisocode"] == "ENG"]
    print('\tRemaining: {} ({}%)'.format(len(cases), 100 * float(len(cases)) / total ))
    print(' - Keep only cases with a judgment document:')
    cases = [i for i in cases if i["doctype"] == "HEJUD"]
    print('\tRemaining: {} ({}%)'.format(len(cases), 100 * float(len(cases)) / total ))
    print(' - Remove cases without an attached document:')
    cases = [i for i in cases if i["application"].startswith("MS WORD")]
    print('\tRemaining: {} ({}%)'.format(len(cases), 100 * float(len(cases)) / total ))
    print(' - Keep cases with a clear conclusion:')
    cases = [i for i in cases if "No-violation" in i["conclusion"] or "No violation" in i["conclusion"] or "Violation" in i["conclusion"] or "violation" in i["conclusion"]]
    print('\tRemaining: {} ({}%)'.format(len(cases), 100 * float(len(cases)) / total ))
    print(' - Remove a specific list of cases hard to process:')
    cases = [i for i in cases if i['itemid'] not in ["001-154354", "001-108395", "001-79411"]]
    print('\tRemaining: {} ({}%)'.format(len(cases), 100 * float(len(cases)) / total ))

    return cases

def generate_statistics(cases):
    """Generate statistics about the cases

        :param cases: list of cases
        :type cases: [dict]
        :return: statistics about the cases
        :rtype: dict
    """
    def generate_count(k, cases):
        s = []
        for c in cases:
            if k == 'conclusion':
                # We do not take into account mention and details
                s.extend([a['element'] for a in c[k]])
            else:
                if type(c[k]) == list:
                    if len(c[k]):
                        s.extend(c[k])
                elif type(c[k]) == str: #string
                    if len(c[k].strip()):
                        s.append(c[k])
        return s

    keys = cases[0].keys()
    except_k = []
    stats = {'attributes':{}}
    for k in [i for i in keys if i not in except_k]:
        s = generate_count(k, cases)
        #print(s)
        s = Counter(s)
        print(' - Attribute "{}": \n\t- Cardinal: {}\n\t- Density: {}'.format(k, len(s), float(len(s)) / len(cases)))
        stats['attributes'][k] = {
            'cardinal': len(s),
            'density': float(len(s)) / len(cases)
        }

    return stats


def main(args):
    input_folder = path.join(args.build, 'raw_cases_info')
    output_folder = path.join(args.build, 'cases_info')
    try:
        if args.f:
            shutil.rmtree(output_folder)
        mkdir(output_folder)
    except Exception as e:
        print(e)
        exit(1)

    cases = []
    files = [path.join(input_folder, f) for f in listdir(input_folder) if path.isfile(path.join(input_folder, f)) if '.json' in f]
    for p in files:
        try:
            with open(p, 'r') as f:
                content = f.read()
                index = json.loads(content)
                cases.extend(index["results"])
        except Exception as e:
            print(p, e)
    cases = [c["columns"] for c in cases]

    print('# Filter cases')
    cases = filter_cases(cases)
    print('# Format cases')
    cases = format_cases(cases)

    print('# Generate statistics')
    stats = generate_statistics(cases)

    with open(path.join(output_folder, 'filter.statistics.json'), 'w') as outfile:
        json.dump(stats, outfile, indent=4, sort_keys=True)

    with open(path.join(output_folder, 'raw_cases_info_all.json'), 'w') as outfile:
        json.dump(cases, outfile, indent=4, sort_keys=True)


    filtered_cases = []
    for c in cases:
        classes = []
        for e in c['conclusion']:
            if e['type'] in ['violation', 'no-violation']:
                if 'article' in e:
                    g = e['article']
                    classes.append('{}:{}'.format(g, 1 if e['type'] == 'violation' else 0))

        classes = list(set(classes))
        opposed_classes = any([e for e in classes if e.split(':')[0]+':'+ str(abs(1 - int(e.split(':')[-1]))) in classes])
        if len(classes) > 0 and not opposed_classes:
            filtered_cases.append(c)

    outcomes = {}
    cases_per_articles = {}
    for i, c in enumerate(filtered_cases):
        ccl = c['conclusion']
        for e in ccl:
            if e['type'] in ['violation', 'no-violation']:
                #print(c['itemid'], e)
                if e['article'] not in outcomes:
                    outcomes[e['article']] = {
                        'violation': 0,
                        'no-violation': 0,
                        'total': 0
                    }
                outcomes[e['article']][e['type']] += 1
                outcomes[e['article']]['total'] += 1
                if e['article'] not in cases_per_articles:
                    cases_per_articles[e['article']] = []
                cases_per_articles[e['article']].append(c)

    print('# Generate case info for specific articles:')
    multilabel_cases = []
    multilabel_index = set()
    for k in outcomes.keys():
        print(' - Generate case info for article {}'.format(k))
        with open(path.join(output_folder, 'raw_cases_info_article_{}.json'.format(k)), 'w') as outfile:
            json.dump(cases_per_articles[k], outfile, indent=4, sort_keys=True)
        multilabel_cases.extend(cases_per_articles[k])
        for c in cases_per_articles[k]:
            multilabel_index.add(c['itemid'])

    multilabel_cases_unique = []
    for c in multilabel_cases:
        if c['itemid'] in multilabel_index:
            multilabel_cases_unique.append(c)
            multilabel_index.discard(c['itemid'])

    with open(path.join(output_folder, 'raw_cases_info_multilabel.json'.format(k)), 'w') as outfile:
        json.dump(multilabel_cases_unique, outfile, indent=4, sort_keys=True)


    multiclass_index = {} # Key: case ID / Value = number of different dataset it appears in
    multiclass_cases = []
    sorted_outcomes = dict(sorted(outcomes.items(), key=lambda x: x[1]['total'])).keys()
    for k in sorted_outcomes:
        for c in cases_per_articles[k]:
            if c['itemid'] not in multiclass_index:
                nb_datasets = [e['article'] for e in c['conclusion'] if 'article' in e]
                if  len(list(set(nb_datasets))) == 1:
                    for cc in c['conclusion']:
                        if 'article' in cc and cc['article'] == k:
                            c['mc_conclusion'] = [cc]
                            break
                    if 'mc_conclusion' in c:
                        multiclass_index[c['itemid']] = k
                        multiclass_cases.append(c)
                    else:
                        print('No article found for {}'.format(c['itemid']))
                else:
                    print('Article {} in {} datasets: {}. Skip for multiclass.'.format(c['itemid'],
                        len(set(nb_datasets)),
                        ','.join(list(set(nb_datasets))))
                    )

    with open(path.join(output_folder, 'raw_cases_info_multiclass.json'.format(k)), 'w') as outfile:
        json.dump(multiclass_cases, outfile, indent=4, sort_keys=True)

 
def parse_args(parser):
    args = parser.parse_args()

    # TODO: check args
    return args

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Filter and format ECHR cases information')
    parser.add_argument('--build', type=str, default="./build/echr_database/")
    parser.add_argument('-f', action='store_true')
    args = parse_args(parser)

    main(args)
 
