"""
module for outputting msgpack
"""

import msgpack

def serialize(obj):
    """Outputs the object as msgpack"""
    return msgpack.packb(obj)
