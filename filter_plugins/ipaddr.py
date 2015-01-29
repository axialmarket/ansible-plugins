#!/usr/bin/env python

from ansible import errors
import ipcalc


def ip_offset(a, *args, **kw):
    """
    Given an IP address, return the IP at the specified offset.
    """
    if not args:
        return a

    ip_addr = a
    offset = args[0]

    try:
        float(offset)
    except ValueError:
        raise errors.AnsibleFilterError("Specified offset isn't numeric.")

    # Return the dotted quad of the offsetted address.
    return ipcalc.IP(ipcalc.IP(ip_addr).ip + offset).dq


class FilterModule(object):

    def filters(self):
        return {'ip_offset': ip_offset}
