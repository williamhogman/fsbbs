from twisted.internet import defer

class Thing:
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
            raise RuntimeError("Tried to access nonexiststant thing")


    def __init__(self,ds,tid):
        self.datasource = ds
        # chain that defered onto our new one
        if tid > 0:
            self.update = True # changes will cause and update
            self.ready = self.loadThing(tid).addCallback(self.ready.callback)
        else:
            self.update = False # changes will cause creation
            # we are already ready so make it a prefired deferred
            self.ready = defer.succeed()


class Container(Thing):
    """ A think containing a sorted set of other things"""
    def __init__(self,ds,tid):
        super(Container,self).__init__(ds,tid)
        @defer.inlineCallbacks
        def onReady(a):
            self.contents = yield self.datasource.zrange(self._key("contents"))
        self.ready.addCallback(onRead)
        
    @defer.inlineCallbacks
    def add(self,thing,score=0):
        """ adds a pointer to the passed in thing"""
        self.contents.append(thing)
        yield self.datasource.zadd(self._key("contents"),score,thing)

class Topic(Container):
    def __init__(self,ds,tid):
        super(Topic,self).__init__(ds,tid)
        def onReady(a):
            # the original post that started the topic
            self.original_post = yield self._get("original_post")
        self.ready.addCallback(onRead)
