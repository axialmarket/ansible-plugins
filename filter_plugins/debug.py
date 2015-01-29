#!/usr/bin/env python
import pdb

def debug_trace(a, *args, **kwargs):
    """
    Run a PDB trace.
    """
    pdb.set_trace()
    return []

class FilterModule(object):
    def filters(self):
        return {'debug_trace': debug_trace}
