""" module for outputting json """

import json

encode = json.dumps
decode = json.loads


def handler(obj):
    """handles complex data types, just dates for now."""
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    else:
        raise TypeError('Object of type %s with value of %s is not JSON serializable' % (type(obj), repr(obj)))

def serialize(obj):
    """serializes the object in the json format"""
    return encode(obj,default=handler)
