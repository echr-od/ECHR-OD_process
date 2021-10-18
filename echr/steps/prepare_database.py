import argparse
import json
import os
from os import listdir
from os.path import isfile
import shutil
from genson import SchemaBuilder
from enum import Enum
import copy
import flatdict
import pandas as pd
import numpy as np
from collections import OrderedDict
from functools import reduce  # forward compatibility for Python 3
import operator
import sys

from echr.utils.folders import make_build_folder
from echr.utils.cli import TAB
from echr.utils.logger import getlogger
from rich.markdown import Markdown
from rich.console import Console

log = getlogger()

__console = Console(record=True)

DELIMITER = '.'

type_priority = OrderedDict([
    ('number', float),
    ('integer', int),
    ('string', str)
])


class COL_HINT(str, Enum):
    HOT_ONE = 'hot_one'
    POSITIONAL = 'positional'


def format_structured_json(cases_list):
    res = []
    representents = {}
    extractedapp = {}
    scl = {}
    decision_body = {}
    for name in cases_list:
        with open(name, 'r') as f:
            c = json.load(f)
        c['representedby'] = [r for r in c['representedby'] if r != 'N/A']
        representents[c['appno']] = {'representedby': c['representedby']}
        extractedapp[c['appno']] = {'appnos': c['extractedappno']}
        decision_body[c['appno']] = {
            'name': [e['name'] for e in c['decision_body']],
            'role': {e['name']: e['role'] for e in c['decision_body'] if 'role' in e}
        }
        scl[c['appno']] = {'scl': c['scl']}

        c['respondent'] = c['respondent'].split(';')  #
        c['applicability'] = c['applicability'].strip().split(';')
        c['appno'] = c['appno'].split(';')[0]
        c['decisiondate'] = c['decisiondate'].split(' ')[0]
        c['judgementdate'] = c['judgementdate'].split(' ')[0]
        c['introductiondate'] = c['introductiondate'].split(' ')[0]
        c['kpdate'] = c['kpdate'].split(' ')[0]
        c['separateopinion'] = True if c['separateopinion'] == 'TRUE' else False

        del c['representedby']
        del c['extractedappno']
        del c['decision_body']
        del c['scl']
        del c['documents']
        del c['content']
        del c['externalsources']
        del c['kpthesaurus']
        del c['__conclusion']
        del c['__articles']
        if not len(c['issue']):
            del c['issue']
        else:
            c['issue'] = sorted(c['issue'])
        if not len(c['applicability']):
            del c['applicability']
        res.append(c)
    return res, representents, extractedapp, scl, decision_body


def get_by_path(root, items):
    return reduce(operator.getitem, items, root)


def set_by_path(root, items, value):
    get_by_path(root, items[:-1])[items[-1]] = value


def determine_schema(X):
    builder = SchemaBuilder()
    for x in X:
        builder.add_object(x)
    schema = builder
    return schema


def get_flat_type_mapping(flat_schema):
    flat_type_mapping = {}
    for k in flat_schema.keys():
        if k.endswith(DELIMITER + 'type'):
            key = k.replace('properties' + DELIMITER, '').replace(DELIMITER + 'type', '')
            flat_type_mapping[key] = flat_schema[k]
    return flat_type_mapping


def get_flat_domain_mapping(X, flat_type_mapping):
    flat_domain_mapping = {}
    for x in X:
        flat = flatdict.FlatterDict(x, delimiter='.')
        for k in flat_type_mapping.keys():
            v = flat.get(k)
            if v is not None:
                if k not in flat_domain_mapping:
                    flat_domain_mapping[k] = set()
                type_ = flat_type_mapping[k]
                try:
                    if type_ == 'array':
                        flat_domain_mapping[k].update(get_by_path(x, k.split('.')))
                    else:
                        flat_domain_mapping[k].add(get_by_path(x, k.split('.')))
                except:
                    if not flat_domain_mapping[k]:
                        del flat_domain_mapping[k]
    for k in flat_domain_mapping:
        flat_domain_mapping[k] = list(flat_domain_mapping[k])
    return flat_domain_mapping


def flatten_dataset(X, flat_type_mapping, schema_hints=None):
    if schema_hints is None:
        schema_hints = {}
    flat_X = []
    for x in X:
        flat = flatdict.FlatterDict(x, delimiter=DELIMITER)
        c_x = copy.deepcopy(x)
        for k in flat_type_mapping.keys():
            col_type = schema_hints.get(k, {}).get('col_type')
            if col_type not in [None, COL_HINT.POSITIONAL]:
                continue
            v = flat.get(k)
            if v is not None:
                sort = schema_hints.get(k, {}).get('sort', False)
                if sort:
                    type_ = flat_type_mapping[k]
                    if type_ == 'array':
                        item_types = flat_type_mapping.get(k + '.items')
                        a = get_by_path(c_x, k.split('.'))
                        if isinstance(item_types,  list):
                            try:
                                a = sorted(a)
                            except:
                                print('# Warning: mix-type array with types: {}'.format(', '.join(item_types)))
                                print('# Warning; no comparison operator provided. Try to assess the proper cast...')
                                for t in type_priority:
                                    try:
                                        a = list(map(type_priority[t], a))
                                        print('# Casting \'{}\' to {}'.format(k, t))
                                        break
                                    except:
                                        log.error('Could not cast \'{}\' to {}'.format(k, t))
                                else:
                                    print('# Error: Could not find any way to sort {}'.format(k))
                                    raise Exception('Could not find any way to sort {}'.format(k))
                            set_by_path(c_x, k.split('.'), sorted(a))
                flat = flatdict.FlatterDict(c_x, delimiter=DELIMITER)
        flat_X.append(flat)
    return flat_X


def hot_one_encoder_on_list(df, column):
    v = [x if isinstance(x, list) else [] for x in df[column].values]
    l = [len(x) for x in v]
    f, u = pd.factorize(np.concatenate(v))
    n, m = len(v), u.size
    i = np.arange(n).repeat(l)

    dummies = pd.DataFrame(
        np.bincount(i * m + f, minlength=n * m).reshape(n, m),
        df.index, map(lambda x: str(column) + '=' + str(x), u)
    )
    return df.drop(column, 1).join(dummies)


def normalize(X, schema_hints=None):
    if schema_hints is None:
        schema_hints = {}

    def hot_one_encoder(df, columns):
        return pd.get_dummies(df, prefix_sep="=", columns=columns)

    schema = determine_schema(X)
    flat_schema = flatdict.FlatDict(schema.to_schema(), delimiter=DELIMITER)
    flat_type_mapping = get_flat_type_mapping(flat_schema)
    flat_domain_mapping = get_flat_domain_mapping(X, flat_type_mapping)
    flat_X = flatten_dataset(X, flat_type_mapping, schema_hints)
    columns_to_encode = [k for k, v in schema_hints.items() if v['col_type'] == COL_HINT.HOT_ONE]
    df = pd.DataFrame(flat_X)
    for c in df.columns:
        f = next((k for k in columns_to_encode if c.startswith(k)), None)
        if f:
            df = df.drop(c, 1)
    encoded = []
    for c in columns_to_encode:
        type_ = flat_type_mapping[c]
        if type_ == 'array':
            if c == 'conclusion':
                articles = set()
                for x in X:
                    for e in x[c]:
                        if 'article' in e:
                            articles.add(e['article'])
                articles = sorted(articles)
                df2 = []
                for x in X:
                    e = []
                    xart = {v['article']: v['type'] for v in x['conclusion'] if 'article' in v}
                    for a in articles:
                        v = 0
                        if a in xart:
                            if xart[a] == 'violation':
                                v = 1
                            else:
                                v = -1
                        e.append(v)
                    df2.append(e)
                df2 = pd.DataFrame(df2, columns=list(map(lambda x: 'ccl_article={}'.format(x), articles)))
                encoded.append(df2)
            else:
                df2 = pd.DataFrame(X)[[c]]
                e = hot_one_encoder_on_list(df2, c)
                encoded.append(e)
        else:
            df2 = pd.DataFrame(X)[c]
            e = hot_one_encoder(df2, [c])
            encoded.append(e)
    df = pd.concat([df] + encoded, axis=1)
    return df, schema, flat_schema, flat_type_mapping, flat_domain_mapping


def run(console, build, title, output_prefix='cases', force=False):
    __console = console
    global print
    print = __console.print

    print(Markdown("- **Step configuration**"))
    print(TAB + "> Prepare release folder structure")
    paths = ['unstructured', 'structured', 'raw']
    for p in paths:
        make_build_folder(console, os.path.join(build, p), force, strict=False)

    print(Markdown("- **Normalize database**"))
    input_folder = os.path.join(build, 'raw', 'preprocessed_documents')
    cases_files = [os.path.join(input_folder, f) for f in listdir(input_folder)
                   if isfile(os.path.join(input_folder, f)) and '.json' in f]

    print(TAB + "> Prepare unstructured cases [green][DONE]")
    # Unstructured
    with open(os.path.join(build, 'unstructured', 'cases.json'), 'w') as outfile:
        outfile.write('[\n')
        for i, f in enumerate(cases_files):
            with open(f) as json_file:
                data = json.load(json_file)
                json.dump(data, outfile, indent=4)
                if i != len(cases_files) - 1:
                    outfile.write(',\n')
        outfile.write('\n]')

    # Structured
    print(TAB + "> Generate flat cases [green][DONE]")
    flat_cases , representatives, extractedapp, scl, decision_body = format_structured_json(cases_files)
    print(TAB + "> Flat cases size: {}MiB".format(sys.getsizeof(flat_cases) / 1000))
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

    output_path = os.path.join(build, 'structured')
    with open(os.path.join(output_path, 'flat_cases.json'), 'w') as outfile:
        json.dump(flat_cases, outfile, indent=4)

    with open(os.path.join(output_path, 'schema_hint.json'), 'w') as outfile:
        json.dump(schema_hints, outfile, indent=4)

    X = flat_cases
    df, schema, flat_schema, flat_type_mapping, flat_domain_mapping = normalize(X, schema_hints)
    df.to_json(os.path.join(output_path, '{}.json'.format(output_prefix)), orient='records')
    df.to_csv(os.path.join(output_path, '{}.csv'.format(output_prefix)))

    json_files = [
        ('schema', schema.to_schema()),
        ('flat_schema', flat_schema.as_dict()),
        ('flat_type_mapping', flat_type_mapping),
        ('flat_domain_mapping', flat_domain_mapping)
    ]
    for f in json_files:
        with open(os.path.join(output_path, '{}_{}.json'.format(output_prefix, f[0])), 'w') as outfile:
            json.dump(f[1], outfile, indent=4)

    os.remove(os.path.join(output_path, 'flat_cases.json'))
    os.remove(os.path.join(output_path, 'cases_flat_schema.json'))
    os.remove(os.path.join(output_path, 'cases_flat_type_mapping.json'))

    print(TAB + '> Generate appnos matrice [green][DONE]')
    matrice_appnos = {}
    for k, v in extractedapp.items():
        matrice_appnos[k] = {e:1 for e in v['appnos']}
    with open(os.path.join(output_path, 'matrice_appnos.json'), 'w') as outfile:
        json.dump(matrice_appnos, outfile, indent=4)

    print(TAB + '> Generate scl matrice [green][DONE]')
    matrice_scl = {}
    for k, v in scl.items():
        matrice_scl[k] = {e: 1 for e in v['scl']}
    with open(os.path.join(output_path, 'matrice_scl.json'), 'w') as outfile:
        json.dump(matrice_scl, outfile, indent=4)

    print(TAB + '> Generate representatives matrice [green][DONE]')
    matrice_representedby = {}
    for k, v in representatives.items():
        matrice_representedby[k] = {e: 1 for e in v['representedby']}
    with open(os.path.join(output_path, 'matrice_representatives.json'), 'w') as outfile:
        json.dump(matrice_representedby, outfile, indent=4)

    print(TAB + '> Generate decision body matrice [green][DONE]')
    matrice_decision_body = {}
    for k, v in decision_body.items():
        matrice_decision_body[k] = {k:v for k,v in v['role'].items()}
    with open(os.path.join(output_path, 'matrice_decision_body.json'), 'w') as outfile:
        json.dump(matrice_decision_body, outfile, indent=4)

    print(TAB + '> Create archives [green][DONE]')
    # Raw
    shutil.make_archive(os.path.join(build, 'raw', 'judgments'), 'zip',
                        os.path.join(build, 'raw', 'judgments'))

    # All
    from zipfile import ZipFile
    with ZipFile(os.path.join(build, 'all.zip'), 'w') as zipObj:
        # Iterate over all the files in directory
        folders = ['unstructured', 'raw', 'structured']
        for f in folders:
            for folderName, _, filenames in os.walk(os.path.join(build, f)):
                for filename in filenames:
                    if not filename.endswith('.zip'):
                        filePath = os.path.join(folderName, filename)
                        zipObj.write(filePath)

def main(args):
    console = Console(record=True)
    run(console,
        build=args.build,
        title=args.title,
        force=args.f)


def parse_args(parser):
    args = parser.parse_args()

    # Check path
    return args


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Normalize any databse of arbitrarily nested documents.')
    parser.add_argument('--build', type=str, default="./build/echr_database/")
    parser.add_argument('--title', type=str)
    parser.add_argument('--schema_hints', type=str)
    parser.add_argument('--output_prefix', type=str)
    parser.add_argument('-f', action='store_true')
    parser.add_argument('-u', action='store_true')
    args = parse_args(parser)

    main(args)

