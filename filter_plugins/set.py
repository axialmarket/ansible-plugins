#!/usr/bin/env python
'Filters for set-related operations'

from collections import Iterable


def is_subset(a, *args, **kw):
    """
    Return True if the first list is a subset of the second.
    first | is_subset(second)
    """
    if not args or not isinstance(args, Iterable):
        return False

    first = a
    second = args[0]

    if not isinstance(first, Iterable) or not isinstance(second, Iterable):
        return False

    return set(first) <= set(second)


class FilterModule(object):

    def filters(self):
        return {'is_subset': is_subset}
