from twisted.internet import defer
from twisted.python import log
from fsbbs.data import datasource
from fsbbs.data.types import RHash

class Thing(object):
    """ Base class for all stored objects in the datastore that are not part of the auth system"""

    def _key(self,name):
        """ returns a string for use in datastore calls"""
        return self._key_cache+name



    
    def _get(self,name):
        """ private, get a key stored for this thing"""
        return self.datasource.get(self._key(name))

    def _mget(self,*args):
        """ gets multiple stored keys in a single request"""
        def conv(args):
            for a in args:
                yield self._key(str(a))

        return self.datasource.mget(list(conv(args)))

    def _set(self,name,val):
        """ private, sets a key stored for this thing"""
        return self.datasource.set(self._key(name),val)


    def __repr__(self):
        return self.type

    def _hash_key(self):
        return self._hash_key_cache

    @property
    def tid(self):
        """ gets the id of this thing"""
        return self._tid

    @tid.setter
    def tid(self,value):
        """ updates the cache when the tid is changed """
        self._tid = value
        self._key_cache = "thing:"+str(self._tid)+":"
        self._hash_key_cache = "thing:"+str(self._tid)
    
    

    def asDict(self,bs=None,**kwargs):
        """ 
        returns a deferred called when the dict has been created. this function is blocking
        and not async but it doesn't matter because it just reads from memory
        """
        d = {"id": self.tid,"type": self.type}
        if bs is None:
            return defer.succeed(d)
        else:
            bs.update(d)
            return defer.succeed(bs)
        
    @defer.inlineCallbacks
    def newThing(self,t=None):
        """ saves a new thing to the datastore"""
        self.tid = yield self.datasource.incr("thing:next_tid")
        log.msg("new {} got tid {}".format(t,self.tid))
        self.type = t
        
        if t is not None:
            yield self._set("type",t)
            


    @defer.inlineCallbacks
    def loadThing(self,tid):
        self.tid = tid
        self.hash = RHash(self._hash_key,self.datasource)
        # load it unless it hasn't been yet
        if not hasattr(self,"type"):
            self.type = yield self._get("type")
        if self.type is None:
            raise ThingNotFoundError("Tried to access nonexiststant thing")


    def __init__(self,tid,ds=None,pretype=None):
        """
        creates a new instance of a thing
        don't actually call this outside the datalayer unless you know what you are doing
        """
        self.datasource = ds
        if pretype is not None:
            self.type = pretype
        if self.datasource is None:
            self.datasource = datasource.getDatasource()
            
        # chain that defered onto our new one
        if tid > 0:
            self.ready = defer.Deferred()
            self.update = True # changes will cause and update
            self.loadThing(tid).chainDeferred(self.ready)
        else:
            self.update = False # changes will cause creation
            # we are already ready so make it a prefired deferred
            self.ready = defer.succeed(None)
