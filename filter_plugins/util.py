#!/usr/bin/env python
'Utility and miscallaneous filters'


from ansible import errors
from collections import Iterable, Mapping
from itertools import chain, cycle
import re

is_iterable = lambda v: isinstance(v, Iterable)

def select_keyval(a, *args, **kwargs):
    """
    Given a list of dictionaries, return the dictionaries that have the
    specified key and value.
    """
    if not a:
        return a

    if not is_iterable(a):
        raise errors.AnsibleFilterError('Expecting an iterable.')

    keyval_pair = (kwargs.get('key'), kwargs.get('value'))

    def test_dict(d):
        return bool(keyval_pair == (keyval_pair[0], d[keyval_pair[0]]))

    return filter(test_dict, a)
    
def filter_matches_in_list(value=[], pattern='', ignorecase=False):
    """
    Given a list, return a sub-list of items matching the provided regex.
    """
    results = list()

    flags = re.I if ignorecase else 0
    repattern = re.compile(pattern, flags=flags)

    for item in value:
        if re.match(repattern, item):
            results.append(item)

    return results


def flatten_list(a, *args, **kwargs):
    """
    Given a list of lists, return a single, flattened list.
    """
    if not a:
        return a

    if not is_iterable(a):
        raise errors.AnsibleFilterError('Expecting an iterable.')

    return list(chain(*a))


def tags_dict_to_string(a, *args, **kwargs):
    '''
    Given a dictionary of instance tags, convert them into a comma seperated
    string, where each tag appears in the form "key=value"
    '''
    if not a:
        return

    if not isinstance(a, Mapping):
        raise errors.AnsibleFilterError(
            'Expecting a dictionary or mapping type.')

    return ', '.join(map('='.join, a.items()))


def itercycle(a, *args, **kwargs):
    '''
    Return cycle iterator for argument.
    '''
    return cycle(args)


def distribute_over(a, *args, **kwargs):
    """
    Distribute the incoming array over the given one.
    """
    if not is_iterable(args) or not args or not is_iterable(args[0]):
        raise errors.AnsibleFilterError(
            'Expecting a single list of items to iterate over.')

    if not is_iterable(a):
        raise errors.AnsibleFilterError(
            'Inbound item to this filter must be a list.')

    return zip(a, cycle(args[0]))

def list_merge(a, *args, **kwargs):
    if not args or not is_iterable(args[0]):
        raise errors.AnsibleFilterError('First argument must be a list.')
    return list(args[0]) + list(a or [])

class FilterModule(object):

    def filters(self):
        return {
            'distribute_over': distribute_over,
            'filter_matches_in_list': filter_matches_in_list,
            'flatten_list': flatten_list,
            'select_keyval': select_keyval,
            'tags_dict_to_string': tags_dict_to_string,
            'itercycle': itercycle,
            'list_merge': list_merge}
