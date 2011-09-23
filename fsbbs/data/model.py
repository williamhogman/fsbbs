from twisted.internet import defer
import datasource 


class ThingNotFoundError(RuntimeError):
    """ error to be raised when a thing cannot be found """


class Thing(object):
    """ Base class for all stored objects in the datastore that are not part of the auth system"""

    def _key(self,name):
        """ returns a string for use in datastore calls"""
        return "thing:{}:{}".format(self.tid,name)
    
    def _get(self,name):
        """ private, get a key stored for this thing"""
        return self.datasource.get(self._key(name))
    def _set(self,name,val):
        """ private, sets a key stored for this thing"""
        return self.datasource.set(self._key(name))
        return self.datasource.set("thing:{}:{}".format(self.tid,name),val)

    def __repr__(self):
        return self.type

    def asDict(self,bs=None):
        d = {"id": self.tid,"type": self.type}
        if bs is None:
            return d
        else:
            bs.update(d)
            return bs
        

    def newThing(self,t=None):
        """ saves a new thing to the datastore"""
        self.tid = yield self.datasource.incr("thing:next_tid")
        self.type = t
        
        if t is not None:
            yield self._set("type",t)
            
        
    @defer.inlineCallbacks
    def loadThing(self,tid):
        self.tid = tid
        self.type = yield self._get("type")
        if self.type is None:
            raise ThingNotFoundError("Tried to access nonexiststant thing")


    def __init__(self,tid,ds=None):
        self.datasource = ds
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
            self.ready = defer.succeed()


class Container(Thing):
    """ A thing containing a sorted set of other things"""
    def __init__(self,tid,ds=None):
        super(Container,self).__init__(tid,ds)
        @defer.inlineCallbacks
        def onReady(a):
            self.contents = yield self.datasource.zrange(self._key("contents"))
        self.ready.addCallback(onReady)
        
    @defer.inlineCallbacks
    def add(self,thing,score=0):
        """ adds a pointer to the passed in thing"""
        self.contents.append(thing)
        yield self.datasource.zadd(self._key("contents"),score,thing)

    def asDict(self,bs=None):
        d = {"contents": self.contents }
        super(Container,self).asDict(d)
        if bs is None:
            return d
        else:
            bs.update(d)
            return bs

class Topic(Container):
    """ A topic is a list of post with one original post and poster"""
    def __init__(self,tid,ds=None):
        super(Topic,self).__init__(tid,ds)
        @defer.inlineCallbacks
        def onReady(a):
            # the original post that started the topic
            self.original_post = yield self._get("original_post")
        self.ready.addCallback(onRead)

class Post(Thing):
    """ A post """
    def __init__(self,tid,ds=None):
        super(Post,self).__init__(tid,ds)
        @defer.inlineCallbacks
        def onReady(a):
            self.poster_uid = yield self._get('poster_uid')
            self.poster_name = yield self.datasource.get("user:{}:username".format(poster_uid))
        
