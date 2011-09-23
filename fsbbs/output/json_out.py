""" module for outputting json """



# ujson is the fastest library 
try:
    import ujson
except ImportError:
    try:
        import json # builtin json
    except ImportError:
        # older versions didn't ship with json. the newer api provides the same functions as simplejson does
        import simplejson as json 
    
    # first class functions  FTW :)
    encode = json.dumps
    decode = json.loads
else:
    encode = ujson.encode
    decode = ujson.decode
    




def serialize(obj):
    return obj
    
    
