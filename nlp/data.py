import csv
import io
# encoding: utf-8

def load_text_file(path, limit=None):
    with io.open(path, 'r', encoding="utf-8") as f:
        content = f.read()
    return content

def load_CSV(path, columns=None):
    content = []
    with open(path, newline='') as file:
        reader = csv.reader(file, delimiter=',', quotechar='"')
        for row in reader:
            if columns is None:
                content.append(row)
            else:
                partial_row = [e for i, e in enumerate(row) if i in columns]
                content.append(partial_row)
    return content


def data_transformations(data, columns_to_index):
    indexes = []
     
    for i in range(len(columns_to_index)):
        indexes.append(set())

    for k, row in enumerate(data):
        for i, j in enumerate(columns_to_index):
            indexes[i].add((row[j], k))

    return indexes

def filter_per_inhabitants(data, n=None):
    i = -1 # Inhabitant column is the last one
    if n is None:
        return data
    return [e for e in data if int(e[i]) > n]


def match_city(indexes, token):
    for index in indexes:
        matches = [i[1] for i in index if i[0] == token]
        if len(matches):
            return matches
    return []


def department_name(data, number):
    '''
    Small trick not to look into the whole file.
    To be changed if the underlying datafile changes!
    '''
    try:
        if number in ['2a', '2A']:
            return data[19]
        elif number in ['2b', '2B']:
            return data[20]
        else:
            n = int(number)
            if n < 20:
                return data[n-1][1]
            elif n > 20:
                return data[n][1]
            else:
                return 'NULL'
    except Exception as e:
        return 'NULL'

def max_n_gram(data, column):
    max_n_gram = 0
    for row in data:
        n = len(row[column].split())
        max_n_gram = max_n_gram if max_n_gram > n else n
    return n


if __name__ == '__main__':

    data_file = 'data/villes_france.csv'
    content = load_CSV(data_file, [0,1,2,3,4,5,6,7,10,14])

    '''
    indexes = data_transformations(content, columns_to_index=[4,2,3,5])
    print(max_n_gram(content, 4))
    matches = match_city(indexes, 'Aix-en-Provence')
    #for i in matches:
    #    print(content[i])
    '''
    import re
    data_original = load_text_file('input_utf8.txt')
    import bisect

    # Generate the index
    boundaries = []
    mapping = []
    counter = 0
    for r in data_original:
        counter += len(r)
        boundaries.append(counter)
        counter += 1 # Space for join
        mapping.append(None)

    data = ' '.join(data_original).replace("'", ' ')
    for i, row in enumerate(content):
        r = (m.start() for m in re.finditer('\s{}\s'.format(row[4]), data))
        #print('{}/{} - {}'.format(i, len(content), row[4]))
        for j in r:
            #print(data[j+1:j+len(row[4])+1])
            k = bisect.bisect_left(boundaries, j+1)
            #print(k, data_original[k])
            if mapping[k] is None:
                mapping[k] = (j, len(row[4]), i)
            else: # is the new match overlapping or longer ?
                if data[mapping[k][0]+1:j+mapping[k][1]+1] in data[j+1:j+len(row[4])+1]:
                    #print('{} -> {}'.format(data[mapping[k][0]+1:j+mapping[k][1]+1], data[j+1:j+len(row[4])+1]))
                    mapping[k] = (j, len(row[4]), i)

    for k, r in enumerate(mapping):
        if r is not None:
            print(k, data_original[k], data[r[0]+1:r[0]+r[1]+1])

