from functools import reduce
import operator

def get_from_dict(data, keys):
    try:
        return reduce(operator.getitem, keys, data)
    except:
        return None

def get_from_path(data, path, sep='.'):
    return get_from_dict(data, path.split(sep))


def compare_two_lists(list1: list, list2: list) -> bool:
    """
    Compare two lists.
    :param list1: first list.
    :param list2: second list.
    :return:      if there is difference between both lists.
    """
    diff = [i for i in list1 + list2 if i not in list1 or i not in list2]
    result = len(diff) == 0
    return result