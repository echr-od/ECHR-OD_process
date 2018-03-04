import bisect
import copy
import os
import re
import sys
import json
import click

from gensim import corpora, models, similarities

from NLP.data import load_text_file, load_CSV, data_transformations, match_city, department_name, max_n_gram, filter_per_inhabitants
from NLP.preprocessing import rectify_missing_space, prepareText, frequencies, generateNGrams

from nltk.tokenize import word_tokenize
from nltk.util import ngrams

import logging
logging.basicConfig(format='[%(levelname)s] - %(message)s', level=logging.INFO)
log = logging.getLogger(__name__)


def rectify_tokens(content):
    """
        Rectify the tokens from obvious typo mistakes

        :param content: list of strings
        :type content: [str]

        :return: Rectified tokens
        :rtype: [str]
    """
    final_tokens = []
    for token in content:
        rectified_token = token
        # Rectify the missing space after a number
        token_list = token.split()
        for e in token_list:
            r = rectify_missing_space(e)
            if r is not None:
                rectified_token = rectified_token.replace(e, ' '.join(r))
        final_tokens.append(rectified_token)
    return final_tokens

def normalized_step(tokens, path='./', force=False, lemmatization=True):
    """
        Normalize the tokens

        :param tokens: list of strings
        :type tokens: [str]
        :param path: path to write the output in
        :type path: str

        :return: normalized tokens
        :rtype: [str]
    """
    output_file = 'normalized.txt'
    p = os.path.join(path, output_file)
    if not force:
        if os.path.isfile(p):
            raise Exception("The file {} already exists!".format(p))

    normalized_tokens = []
    with open(p, 'w') as file:
        for token in sorted(tokens):
            r = prepareText(token, lemmatization)
            normalized_tokens.append([t[0] for t in r])
            file.write(' '.join([t[0] for t in r]) + '\n')
    return normalized_tokens

def ngram_step(original_tokens, freq=None, path='./', force=False):
    """
        Calculate the ngrams

        :param original_tokens: list of tokens
        :type original_tokens: [[str]]
        :param freq: rules to extract and filter ngrams
        :type freq: dict
        :param path: path to write the output in
        :type path: str

        :return: dictionary of ngrams indexed by n
        :rtype: dict
    """
    if freq is None:
        log.info('No configuration specified, uses the default one')
        freq = {1: 5, 2: 2, 3: 2, 4: 2}

    for k in freq:
        output_file = 'tokens_{}grams.txt'.format(k)
        p = os.path.join(path, output_file)
        if not force:
            if os.path.isfile(p):
                raise Exception("The file {} already exists!".format(p))

    allgrams = frequencies(original_tokens, n=len(freq), minlimits=freq)
    for k, ngrams in allgrams.items():
        tokens = [(n.replace('_', ' '), k) for n,k in ngrams.items()]
        with open(os.path.join(path, 'tokens_{}grams.txt'.format(k)), 'w') as file:
            for token in sorted(tokens, key=lambda x: x[1], reverse=True):
                file.write('{}\t{}\n'.format(token[0], token[1]))

    return allgrams

def locations_step(config, tokens, disambiguation=True, path='./', force=False, nb_hab=None):
    """
        Extract the locations

        :param original_tokens: list of tokens
        :type original_tokens: [[str]]
        :param disambiguation: use the rules to select a city among the multiple choices?
        :type disambiguation: bool
        :param path: path to write the output in
        :type path: str
    """
    def match_patterns(data, dict_data, n_row, boundaries, mapping):
        for i, row in enumerate(dict_data):
            r = [m.start() for m in re.finditer('\s{}\s'.format(row[n_row]), data)]
            sys.stdout.write('[INFO] - {}/{}\r'.format(i+1, len(dict_data)))
            for j in r:
                k = bisect.bisect_left(boundaries, j+1)
                if mapping[k] is None:
                    mapping[k] = (j, len(row[n_row]), i)
                else: # is the new match overlapping or longer ?
                    if data[mapping[k][0]+1:j+mapping[k][1]+1] in data[j+1:j+len(row[n_row])+1]:
                        mapping[k] = (j, len(row[n_row]), i)
            sys.stdout.flush()

    def format_positive_output_city(token, city):
        country = 'France' # Hardcoded for now since the database is only about France
        token_replaced = token
        depart = 'NULL'
        try:
            token_replaced = token.replace(city[4], '#LOCALITE#')
            depart = department_name(depart_data, city[1])
        except Exception as e:
            log.warning('{} : {}'.format(token, e))
        return '{}\t{}\t{}\t{}\t{}\t{}\t{}\n'.format(token, 'Oui', token_replaced, 'France', city[1], depart, city[5])

    def format_positive_output_depart(token, depart):
        country = 'France' # Hardcoded for now since the database is only about France
        token_replaced = token
        token_replaced = token.replace(depart[2], '#LOCALITE#')
        return '{}\t{}\t{}\t{}\t{}\n'.format(token, 'Oui', token_replaced, 'France', depart[1])

    def format_positive_output_region(token, region):
        country = 'France' # Hardcoded for now since the database is only about France
        token_replaced = token
        token_replaced = token.replace(region[1], '#LOCALITE#')
        return '{}\t{}\t{}\t{}\t{}\n'.format(token, 'Oui', token_replaced, 'France', region[0])

    output_file = 'locations.txt'
    p = os.path.join(path, output_file)
    if not force and os.path.isfile(p):
        raise Exception("The file {} already exists!".format(p))

    cities_data = load_CSV(config['cities_file'], [0,1,2,3,4,5,10,14])
    depart_data = load_CSV(config['depart_file'], [1,2,4])
    region_data = load_CSV(config['region_file'], [0,1])

    cities_data = filter_per_inhabitants(cities_data, nb_hab)

    # Generate the index
    boundaries = []
    mapping_cities = []
    mapping_depart = []
    mapping_region = []
    counter = 0
    for r in tokens:
        counter += len(r)
        boundaries.append(counter)
        counter += 1 # Space for join
        mapping_cities.append(None)
        mapping_depart.append(None)
        mapping_region.append(None)

    data = ' '.join(tokens).replace("'", ' ')
    
    log.info('Extract the cities...')
    match_patterns(data, cities_data, 4, boundaries, mapping_cities)
    log.info('Extract the departments...')
    match_patterns(data, depart_data, 2, boundaries, mapping_depart)
    log.info('Extract the regions...')
    match_patterns(data, region_data, 1, boundaries, mapping_region)

    with open(p, 'a') as file:
        for k, r in enumerate(mapping_cities):
            try:
                token = tokens[k]
                if r is not None:
                    file.write(format_positive_output_city(token, cities_data[r[2]]))
            except Exception as e:
                log.warning(e)

    with open(p, 'a') as file:
        for k, r in enumerate(mapping_depart):
            try:
                token = tokens[k]
                if r is not None:
                    depart = depart_data[r[2]][1]
                    city = cities_data[mapping_cities[k][2]][4] if mapping_cities[k] is not None else ''
                    if len(depart) > len(city):
                        file.write(format_positive_output_depart(token, depart_data[r[2]]))
                    else:
                        log.info('City {} found in {} - Skip department {}'.format(city, token, depart))
            except Exception as e:
                log.warning(e)

    with open(p, 'a') as file:
        for k, r in enumerate(mapping_region):
            try:
                token = tokens[k]
                if r is not None:
                    region = region_data[r[2]][0]
                    city = cities_data[mapping_cities[k][2]][4] if mapping_cities[k] is not None else ''
                    depart = depart_data[mapping_depart[k][2]][1] if mapping_depart[k] is not None else ''
                    if len(region) > len(city) and len(region) > len(depart):
                        file.write(format_positive_output_region(token, region_data[r[2]]))
                    elif len(region) <= len(city):
                        log.info('City {} found in {} - Skip region {}'.format(city, token, region))
                    else:
                        log.info('Department {} found in {} - Skip region {}'.format(depart, token, region))
            except Exception as e:
                log.warning(e)

    with open(p, 'a') as file:
        for k, r in enumerate(mapping_cities):
            token = tokens[k]
            if r is None and mapping_depart[k] is None and mapping_region[k] is None:
                    file.write('{}\t{}\n'.format(token, 'Non'))
    

def _locations_step(config, tokens, disambiguation=True, path='./', force=False):
    """
        Extract the locations

        :param original_tokens: list of tokens
        :type original_tokens: [[str]]
        :param disambiguation: use the rules to select a city among the multiple choices?
        :type disambiguation: bool
        :param path: path to write the output in
        :type path: str
    """

    def format_positive_output(token, city):
        country = 'France' # Hardcoded for now since the database is only about France
        token_replaced = token.replace(cities_data[k][4], '#LOCALITE#')
        return '{}\t{}\t{}\t{}\t{}\t{}\t{}\n'.format(token, 'Oui', token_replaced, 'France', city[1], department_name(depart_data, city[1]), city[5])

    output_file = 'cities.txt'
    p = os.path.join(path, output_file)
    if not force and os.path.isfile(p):
        raise Exception("The file {} already exists!".format(p))

    cities_data = load_CSV(config['cities_file'], [0,1,2,3,4,5,10,14])
    depart_data = load_CSV(config['depart_file'], [1,2])
    region_data = load_CSV(config['region_file'], [1,2])

    n = max_n_gram(cities_data, 4)
    r = range(1,n+1)
    freq = dict(zip(r, [1]*len(r)))

    indexes = data_transformations(cities_data, columns_to_index=[4])
    for i, token in enumerate(sorted(tokens)):
        sys.stdout.write('[INFO] - {}/{}\r'.format(i, len(tokens)))
        local_freq = generateNGrams(token.split(), len(freq))
        cities = set()
        for j in range(len(local_freq))[::-1]:
            for gram in local_freq[j + 1]:
                r = set(match_city(indexes, gram.replace('_', ' ').replace('\'', ' ')))
                cities.update(r)
            if len(cities) > 0: # We already found some cities in n grams, no need to check n-1 grams
                break

        cities = list(cities)
        max_hab = 0
        max_i = 0
        for j, c in enumerate(cities):
            hab = 0
            if(len(cities) > 1 and disambiguation):
                try:
                    hab = cities_data[c][-1]
                    hab = 0 if hab == 'NULL' else int(hab)
                except Exception as e:
                    pass
                if max_hab < hab:
                    max_hab = hab
                    max_i = j
        with open(os.path.join(path, output_file), 'a') as file:
            if len(cities):
                if disambiguation:
                    k = cities[max_i]
                    file.write(format_positive_output(token, cities_data[k]))
                else:
                    for k in cities:
                        file.write(format_positive_output(token, cities_data[k]))
            else:
                file.write('{}\t{}\n'.format(token, 'Non'))
        sys.stdout.flush()

@click.command()
@click.option('-i', '--input', nargs=1, required=True)
@click.option('-l', '--limit', nargs=1, required=False)
@click.option('-d', '--disambiguation', is_flag=True)
@click.option('-f', '--force', is_flag=True)
@click.option('-s', '--step', nargs=1, required=False, type=click.Choice(['normalize', 'ngrams', 'locations', 'all']))
@click.option('--hab', nargs=1, required=False, type=int)
@click.option('-nl', '--no-lemmatization', is_flag=True)
def main(input, limit, disambiguation, force, step, hab, no_lemmatization):
    if step is None:
        step = 'all'

    config = None
    try:
        with open('config/config.json') as data:
            config = json.load(data)
            # Basic config validation
            if 'ngrams' not in config:
                raise Exception('Section "ngrams" missing from configuration file')
            else:
                for k in copy.deepcopy(config['ngrams']):
                    config['ngrams'][int(k)] = config['ngrams'][k]
                    del config['ngrams'][k]
    except Exception as e:
        log.error('Cannot load configuration file. Details: {}'.format(e))
        exit(5)

    if not os.path.isfile(input):
        log.error('Cannot find file: {}'.format(input))
        exit(10)

    log.info('Loading input file: {}'.format(input))
    content = []
    try:
        content = load_text_file(input, limit)
        log.info('NUMBER OF FILES: {}'.format(len(content)))
    except Exception as e:
        log.error('Cannot load the input file. Details: {}'.format(e))
        exit(20)

    log.info('Rectifying tokens')
    try:
        content = rectify_tokens(content)
    except Exception as e:
        log.error('Could not rectify tokens. Details: {}'.format(e))
        exit(30)

    if step in ['all', 'normalize', 'ngrams']:
        log.info('Normalize the tokens')
        try:
            normalized_tokens = normalized_step(content, force=force, lemmatization=not no_lemmatization)
        except Exception as e:
            log.error('Could not normalized the tokens. Details: {}'.format(e))
            exit(40)

        if step in ['all', 'ngrams']:
            log.info('Calculate the ngranms and frequencies')
            try:
                all_grams = ngram_step(normalized_tokens, config['ngrams'], force=force)
                texts = []
                for k, v in all_grams.items():
                    texts.append([i for i in v] * k)
                dictionary = corpora.Dictionary(texts)
                corpus = []
                for i, t in enumerate(content):
                    print('{}/{}'.format(i, len(content)))
                    nt = normalized_step([t], force=True, lemmatization=not no_lemmatization)[0]
                    fs = dictionary.doc2bow(nt)
                    #corpus.append(fs)
                    a = []
                    for e in fs:
                        for i in range(1,e[1]+1):
                            a.append("{}0000{}".format(e[0], i))
                        # a.append(str(e[0]))
                    #fs = ["({}_{})".format(f[0], f[1]) for f in fs]
                    #print(fs)
                    corpus.append(' '.join(a))
                with open('casebase.txt', 'w') as file:
                    for l in corpus:
                        #print(l)
                        file.write(l + '\n')
                #tfidf = models.TfidfModel(corpus)
                #for doc in tfidf[corpus]:
                #    print(doc)
                #model = models.LdaModel(tfidf[corpus], id2word=dictionary, num_topics=100)
            except Exception as e:
                log.error('Could not extract the n-grams. Details: {}'.format(e))
                exit(50)

    if step in ['all', 'locations']:
        log.info('Extract the locations')
        try:
            locations_step(config['locations'], content, disambiguation, force=force, nb_hab=hab)
        except Exception as e:
            log.error('Could not extract the locations. Details: {}'.format(e))
            exit(60)



if __name__ == '__main__':
    main()