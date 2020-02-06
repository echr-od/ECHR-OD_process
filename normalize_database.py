from genson import SchemaBuilder
from enum import Enum, auto
import copy
import flatdict
import pandas as pd
import numpy as np
from collections import OrderedDict
import logging
import argparse
import json
import os

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

DELIMITER = '.'

type_priority = OrderedDict([
    ('number', float),
    ('integer', int),
    ('string', str)
])

class COL_HINT(str, Enum):
    HOT_ONE = 'hot_one'
    POSITIONAL = 'positional'

from functools import reduce # forward compatibility for Python 3
import operator


def format_structured_json(cases):
    res = []
    representents = {}
    extractedapp = {}
    scl = {}
    decision_body = {}
    for c in cases:
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
    for x in X:
        for k in x:
            pass
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
                        if type(item_types) == list:
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
                                        continue
                                else:
                                    print('# Error: Could not find any way to sort {}'.format(k))
                                    raise Exception('Could not find any way to sort {}'.format(k))
                            set_by_path(c_x, k.split('.'), sorted(a))
                flat = flatdict.FlatterDict(c_x, delimiter=DELIMITER)
        flat_X.append(flat)
    return flat_X


def hot_one_encoder_on_list(df, column):
    v = [x if type(x) == list else [] for x in df[column].values]
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

    def get_unique_values(X, columns):
        return pd.unique(X[columns].values.ravel('K'))

    def hot_one_encoder(df, columns):
        v = get_unique_values(df, columns)
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
                    xart = {v['article']:v['type'] for v in x['conclusion'] if 'article' in v}
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
    

def test():

    X = [
        {'a': [2, 3, 5], 'b': {'field': 'value', 'nested_array': ['f', 'o', 'o']}, 'c': 1.02, 't': [1,2,3]},
        {'a': [3, 2], 'b': {'field': 'value'}, 'c': 12, 't':[2,3,5]},
        {'a': ['mix', 'a', 3], 'b': {'field': 'another value'}, 'd': [{'b': 'bar'}]},
    ]

    schema_hints = {
        'a': {
            'col_type': COL_HINT.POSITIONAL,
            'sort': True
        },
        'c': {
            'col_type': COL_HINT.HOT_ONE
        },
        't': {
            'col_type': COL_HINT.HOT_ONE
        }
    }

    '''
    DEFAULT OUTPUT: -> Arrays are treated as positional (possibility to sort)
    a.0 | a.1 | a.2 | b.field | b.nested_array.0 | b.nested_array.1 | b.nested_array.2 |    c | d.0.b | 
      2     3     5     value                  f                  0                  0   1.02
      6     7              
      7     5     
    
    OPTIONAL OUTPUT: -> Array are treated as sets with hot-one-encoder
    a.2 | a.3 | a.5 | a.6 | a.7 | b.field | b.nested_array.0 | b.nested_array.1 | b.nested_array.2 | c | d.0.b | 
    
    + panda describe on any level + basic stats (boundary, domain)
    
    '''

def main(args):
    schema_hints = {}
    X = []
    with open(args.schema_hints) as f:
        schema_hints = json.load(f)
    with open(args.database_json) as f:
        X = json.load(f)
    df, schema, flat_schema, flat_type_mapping, flat_domain_mapping = normalize(X, schema_hints)
    output_path = args.build
    df.to_json(os.path.join(output_path, '{}.json'.format(args.output_prefix)), orient='records')
    df.to_csv(os.path.join(output_path, '{}.csv'.format(args.output_prefix)))

    json_files = [
        ('schema', schema.to_schema()),
        ('flat_schema', flat_schema.as_dict()),
        ('flat_type_mapping', flat_type_mapping),
        ('flat_domain_mapping', flat_domain_mapping)
    ]
    for f in json_files:
        with open(os.path.join(output_path, '{}_{}.json'.format(args.output_prefix, f[0])), 'w') as outfile:
            json.dump(f[1], outfile, indent=4)


def parse_args(parser):
    args = parser.parse_args()
    # Check path
    return args


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Normalize any databse of arbitrarily nested documents.')
    parser.add_argument('--build', type=str, default="./build/echr_database/")
    parser.add_argument('--database_json', type=str)
    parser.add_argument('--schema_hints', type=str)
    parser.add_argument('--output_prefix', type=str)
    parser.add_argument('-f', action='store_true')
    parser.add_argument('-u', action='store_true')
    args = parse_args(parser)

    main(args)
