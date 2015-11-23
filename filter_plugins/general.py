#!/usr/bin/env python

from ansible.errors import AnsibleFilterError
from collections import Iterable
import re


def get_required_arg_of_type(arguments, argtype=basestring, typedesc='string'):
    '''
    Given a list, return the first argument if it matches the specified type.

    Raise an AnsibleFilterError if the argument isn't a list to start with,
    it's an empty list, or the element in the list isn't the desired type.
    '''
    if not arguments or not isinstance(arguments, Iterable) or \
            not isinstance(arguments[0], argtype):
        raise AnsibleFilterError(
            'At least a single {} must be specified as the filter argument.'
            .filter(typedesc))
    return arguments[0]


def mapped_call(call, args_list):
    '''
    Given a callable, return the list of each result of the callable applied
    to each member of the args_list.

    Raise an AnsibleFilterError if the given isn't a list or is None.
    '''
    if not args_list or not isinstance(args_list, Iterable):
        raise AnsibleFilterError('Expecting a list or some type of iterable.')
    return map(call, args_list)


def mapped_prefix_filter(a, *args, **kw):
    """
    Filter that adds the given prefix to the beginning of every element in the
    given list.
    """
    prefix = get_required_arg_of_type(args)
    call = lambda thing: prefix + thing
    return mapped_call(call, a)


def mapped_suffix_filter(a, *args, **kw):
    """
    Filter that adds the given suffix to the end of every element in the
    given list.
    """
    suffix = get_required_arg_of_type(args)
    call = lambda thing: thing + suffix
    return mapped_call(call, a)


def get_ending_digits(a, *args, **kw):
    """
    Get the integers from the end of the given string, else return an empty
    string.
    """
    if not a:
        return ""
    m = re.match('.+(\d+)$', a)
    if m:
        return m.groups()[0]
    return ""


class FilterModule(object):

    def filters(self):
        return {
            'map_prefix': mapped_prefix_filter,
            'map_suffix': mapped_suffix_filter,
            'get_ending_digits': get_ending_digits,
        }
