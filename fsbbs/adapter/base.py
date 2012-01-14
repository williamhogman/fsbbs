from functools import partial
import json,sys
from twisted.internet import defer



class _ViewMeta(type):
    def __new__(cls,name,bases,dct):
        upd = dict()
        viewfns = dict()
        for (name,val) in dct.iteritems():
            if hasattr(val,"is_view_field") and val.is_view_field():
                viewfns[name] = val.view_function
            else:
                upd[name] = val

        upd["_viewfns"] = viewfns
        return type.__new__(cls,name,bases,upd)
        
def DefaultView(obj):
    return sys.modules["fsbbs.adapter"].get("Default"+obj.__name__)

class ViewField(object):
    is_view_field = lambda self: True
    def __init__(self,fn):
        self.view_function = fn

def ViewContents():
    @ViewField
    def inner(obj):
        return [DefaultView(sub) for sub in obj.get_contents()]
    return inner

def AttrField(fname):
    @ViewField
    def inner(obj):
        return getattr(obj,fname)
    return inner

    
class View(object):
    """ Baseclass for views """
    __metaclass__ = _ViewMeta
    def __init__(self,obj):
        """ Creates a new view of the passed in object """
        self.obj = obj

    def marshal_as(self,_type):
        if _type == "json":
            return self.as_json()

    def _as_kv_tuple(self):
        for (name,fn) in self._viewfns.iteritems():
            yield (name, fn(self.obj))

    @defer.inlineCallbacks
    def as_processed_dict(self):
        """ returns a deferred with the completed dict once it is ready"""
        op = dict()
        for (k,v) in self._as_kv_tuple():
            if type(v) == defer.Deferred:
                op[k] = (yield v)
            else:
                op[k] = v
        defer.returnValue(op)
    
    def as_dict(self):
        """ returns the view as a dict without waiting for deferreds"""
        return dict(self._as_kv_tuple())

    @defer.inlineCallbacks
    def as_json(self):
        """ returns a deferred callbacking with json for this view"""
        defer.returnValue(json.dump((yield self._processed_dict())))


