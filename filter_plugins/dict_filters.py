#!/usr/bin/env python


from ansible.errors import AnsibleFilterError
from collections import Iterable, Mapping
from functools import partial
from operator import contains, not_
from re import search


is_iterable = lambda v: isinstance(v, Iterable)
is_mapping = lambda v: isinstance(v, Mapping)


def require_mapping(item):
    '''
    Raise AnsibleFilterError if the given item isn't a dict or mapping.
    '''
    if not is_mapping(item):
        raise AnsibleFilterError('Expecting a dictionary or mapping type.')
        

def dict_nonoverwriting_merge(a, *args, **kw):
    """
    Return a merged dictionary, but do not overwrite keys.
    """
    if not args:
        return a

    require_mapping(a)

    result = a.copy()
    r_keys = result.keys()

    for item in args:
        require_mapping(item)
        temp = item.keys()
        colliding_keys = list(set(temp).intersection(r_keys))
        if len(colliding_keys) > 0:
            raise AnsibleFilterError(
                'Cannot merge dictionaries, keys conflict: {}'.format(
                    colliding_keys))
            result.update(item)

    return result


def dict_merge(a, *args, **kw):
    """
    Return a merged dictionary.
    """
    if not args:
        return a

    result = a.copy()

    for item in args:
        require_mapping(item)
        result.update(item)

    return result


def resolve_key(given_dict, key):
    '''
    Given a dict and a key, return its value.

    If the key is in the format 'foo.baz',
    each part separated by '.' is assumed to be a key
    referencing a dictionary nested as the value to the
    preceding part.

    Returns the value found for that key.

    Example:
    {
    'name': 'rserv1',
    'properties:' {
            'type': 'rserver',
        }
    }

    'properties.type' resolves to 'rserver'
    '''
    if not is_mapping(given_dict):
        return None

    if key in given_dict:
        return given_dict[key]

    value = None
    if '.' in key:
        key_hier = key.split('.')
        temp_item = given_dict

        for temp_key in key_hier:

            if is_mapping(temp_item):
                temp_item = temp_item.get(temp_key)
            else:
                temp_item = None
                break

        value = temp_item

    return value


def select_dicts_for_key_with_value_in_list_filter(
        a, *args, **kwargs):
    if not is_iterable(a):
        return list()

    if a and not is_mapping(a[0]):
        raise AnsibleFilterError(
            ''' Expecting a list of dictionaries as input. ''')

    inverted = kwargs.get('inverted', False)

    if not is_iterable(args) or \
            (len(args) < 2) or not is_iterable(args[1]):
        raise AnsibleFilterError(
            'Expects 2 parameters: the key, and the list of'
            'values that should {}match for that key.'
            .format('' if not inverted else 'not '))

    dict_list = a
    key = args[0]
    values_list = args[1]

    return select_dicts_for_key_with_value_in_list(
        dict_list, key, values_list, inverted=inverted)


def select_dicts_with_keyed_value_matching_pattern_filter(
        a, *args, **kwargs):
    '''
    Given a list of dictionaries as incoming filter data, and a key name and
    regular expression as arguments, return a list of dictionaries containing
    a value at the given key matching the given expression.
    '''
    if not is_iterable(a):
        raise AnsibleFilterError('Expecting a list')

    if any(filter(lambda d: not is_mapping(d), a)):
        raise AnsibleFilterError('Expecting a list of dictionaries.')

    if len(args) != 2:
        raise AnsibleFilter((
            'Expecting the key whose value to filter for, and the regular '
            'expression to match the key\'s value against as arguments.'))

    key = args[0]
    pattern = args[1]

    filter_func = partial(search, pattern)

    reverse = kwargs.get('reverse', False)
    op = not_ if reverse else bool

    return filter(lambda d: op(filter_func(resolve_key(d, key) or '')), a)


def select_dicts_with_keyed_value_not_matching_pattern_filter(
        a, *args, **kwargs):
    return select_dicts_with_keyed_value_matching_pattern_filter(
        a, *args, reverse=True, **kwargs)


def select_dicts_for_key_with_value_in_list(
        dict_list, key, values_list, inverted=False):
    '''
    Given a list of dictionaries, a key specifier, and a list of values,
    return the list of dictionaries in the original list where
    the value for the given key specifier is in the list of specified values.

    A "key specifier" is a string which can be a key name, or a specifier
    of the form "foo.bar.baz", where each dot ('.') is used to resolve a key
    in the nested dictionary.

    If inverted is True, selects for keys that do not have their
    corresponding value in the list.
    '''
    op = not_ if inverted else bool
    item_test = lambda item: op(contains(values_list, resolve_key(item, key)))
    return filter(item_test, dict_list)


def sort_dicts_by_key(dict_list, key):
    '''
    Given a list of dictionaries, return a list of them sorted by the value
    they each have at the given key.  Keys in nested dicts can be represented
    as 'key1.key2.key3'
    '''
    keyfunc = lambda x: resolve_key(x, key)
    return sorted(dict_list, key=keyfunc)


class FilterModule(object):

    def filters(self):
        select_dicts_for_key_with_value_not_in_list_filter = partial(
            select_dicts_for_key_with_value_in_list_filter, inverted=True)

        return {
            'select_dicts_for_key_with_value_in_list':
                select_dicts_for_key_with_value_in_list_filter,
            'select_dicts_for_key_with_value_not_in_list':
                select_dicts_for_key_with_value_not_in_list_filter,
            'select_dicts_with_keyed_value_matching_pattern':
                select_dicts_with_keyed_value_matching_pattern_filter,
            'select_dicts_with_keyed_value_not_matching_pattern':
                select_dicts_with_keyed_value_not_matching_pattern_filter,
            'dict_merge': dict_merge,
            'dict_nonoverwriting_merge': dict_nonoverwriting_merge,
            'sort_dicts_by_key': sort_dicts_by_key,
        }
