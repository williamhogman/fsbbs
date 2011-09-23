"""
module for outputting msgpack
"""

import msgpack

def serialize(obj):
    return msgpack.packb(obj)
