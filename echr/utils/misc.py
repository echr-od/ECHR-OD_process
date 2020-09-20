from functools import reduce
import operator

def get_from_dict(data, keys):
    try:
        return reduce(operator.getitem, keys, data)
    except:
        return None

def get_from_path(data, path, sep='.'):
    return get_from_dict(data, path.split(sep))