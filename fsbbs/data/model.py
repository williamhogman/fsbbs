from twisted.internet import defer
from twisted.python import log
import datasource
import datetime
import time


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

    def asDict(self,bs=None,**kwargs):
        """ 
        returns a deferred called when the dict has been created. this function is blocking
        and not async but it doesn't matter because it just reads from memory
        """
        d = {"id": self.tid,"type": self.type}
        if bs is None:
            defer.returnValue(d)
            return defer.succeed(d)
        else:
            bs.update(d)
            return defer.succeed(bs)
        

    def newThing(self,t=None):
        """ saves a new thing to the datastore"""
        self.tid = yield self.datasource.incr("thing:next_tid")
        self.type = t
        
        if t is not None:
            yield self._set("type",t)
            
        
    @defer.inlineCallbacks
    def loadThing(self,tid):
        self.tid = tid
        # load it unless it hasn't been yet
        if not hasattr(self,"type"):
            self.type = yield self._get("type")
        if self.type is None:
            raise ThingNotFoundError("Tried to access nonexiststant thing")


    def __init__(self,tid,ds=None,pretype=None):
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
            self.ready = defer.succeed()


class Container(Thing):
    """ A thing containing a sorted set of other things"""
    def __init__(self,tid,*args,**kwargs):
        super(Container,self).__init__(tid,*args,**kwargs)
        @defer.inlineCallbacks
        def onReady(a):
            self.contents = yield self.datasource.zrange(self._key("contents"))
        self.ready.addCallback(onReady)
        
    @defer.inlineCallbacks
    def add(self,thing,score=0):
        """ adds a pointer to the passed in thing"""
        self.contents.append(thing)
        yield self.datasource.zadd(self._key("contents"),score,thing)

    def get_contents(self):
        defs = list()
        for tid in self.contents:
            ## yo dawg so i herd u liek async!
            # get a thing 
            
            d = anythingFromId(tid,self.datasource,ready=True)

            def onError(err):
                log.msg("Thing {} not found in {}".format(tid,self.tid))
                return False

            d.addErrback(onError)
            defs.append(d)

        dl = defer.DeferredList(defs)
        def process(result):
            res = list()
            for (status, val) in result:
                if status and val:
                    res.append(val)

            return res

        dl.addCallback(process)
        return dl
                    
                

    def _contentsAsDict(self):
        gc = self.get_contents()
        
        def process(val):
            defs = list()
            for c in val:
                defs.append(c.asDict())
            return defer.DeferredList(defs)
        def mergeDicts(result):
            res = list()
            for (status, val) in result:
                if status:
                    res.append(val)
            return res
                   

        gc.addCallback(process)
        gc.addCallback(mergeDicts)
        return gc

    @defer.inlineCallbacks
    def asDict(self,bs=None,contentsParsed=False,**kwargs):
        if contentsParsed:
            
            cnt = yield self._contentsAsDict()
                
            d = {"contents": cnt}
        else:
            d = {"contents": self.contents }
        super(Container,self).asDict(d)
        if bs is None:
            log.msg("bs was none")
            defer.returnValue(d)
        else:
            bs.update(d)

            defer.returnValue(bs)

class Topic(Container):
    """ A topic is a list of post with one original post and poster"""
    def __init__(self,tid,*args,**kwargs):
        super(Topic,self).__init__(tid,*args,**kwargs)
        @defer.inlineCallbacks
        def onReady(a):
            # the original post that started the topic
            self.original_post = yield self._get("original_post")
            self.title = yield self._get("title")
        self.ready.addCallback(onReady)
        
    @defer.inlineCallbacks
    def asDict(self,bs=None,**kwargs):
        d = {"title": self.title}
        s = yield super(Topic,self).asDict(bs=d,**kwargs)
        d.update(s)
        if bs is None:
            defer.returnValue(d)
        else:
            bs.update(d)
            defer.returnValue(bs)


class Post(Thing):
    """ A post """
    def __init__(self,tid,*args,**kwargs):
        super(Post,self).__init__(tid,*args,**kwargs)
        @defer.inlineCallbacks
        def onReady(a):
            self.poster_uid = yield self._get('poster_uid')
            self.poster_name = yield self.datasource.get("user:{}:username".format(self.poster_uid))
            self.text = yield self._get('text')
            self.pubdate_stamp = yield self._get('pubdate')
        self.ready.addCallback(onReady)
    
    @property
    def pubdate(self):
        if self.pubdate_stamp is None:
            return None
        return datetime.datetime.utcfromtimestamp(self.pubdate_stamp)
    @pubdate.setter
    def pubdate(self,value):
        self.pubdate_stamp = time.mktime(value.timetuple())


    @defer.inlineCallbacks
    def asDict(self,bs=None,**kwargs):
        d = {"poster_uid": self.poster_uid,"poster_name": self.poster_name,"text": self.text,"pubdate": self.pubdate}
        s = yield super(Post,self).asDict(bs=d,**kwargs)
        d.update(s)
        if bs is None:
            defer.returnValue(d)
        else:
            bs.update(d)
            defer.returnValue(bs)

class Category(Container):
    """ 
    a category system is a common feature on BBSes it allows for the grouping of content into a 
    basically this is a container with a name
    """
    def __init__(self,*args,**kwargs):
        super(Category,self).__init__(*args,**kwargs)
        @defer.inlineCallbacks
        def onReady(a):
            self.title = yield self._get('title')
            self.description = yield self._get('description')
        self.ready.addCallback(onReady)

    @defer.inlineCallbacks
    def asDict(self,bs=None,**kwargs):
        d = {"title": self.title, 'description': self.description}
        s = yield super(Category,self).asDict(bs=d,**kwargs)
        d.update(s)
        if bs is None:
            defer.returnValue(d)
        else:
            bs.update(d)
            defer.returnValue(bs)
        

class Forum(Container):
    def __init__(self,*args,**kwargs):
        super(Forum,self).__init__(*args,**kwargs)
        @defer.inlineCallbacks
        def onReady(a):
            self.name = yield self._get('name')
            self.tagline = yield self._get('tagline')
        self.ready.addCallback(onReady)
    
    @defer.inlineCallbacks
    def asDict(self,bs=None,minimal=False,**kwargs):
        d = {"name": self.name,"tagline": self.tagline }
        if not minimal:
            s = yield super(Forum,self).asDict(bs=d,**kwargs)
            d.update(s)

        if bs is None:
            defer.returnValue(d)
        else:
            bs.update(d)
            defer.returnValue(bs)



type_to_class = {}

# creating a mapping list between types in the db and our classes
for cls in [Container,Topic,Post,Forum,Category]:
    type_to_class[cls.__name__.lower()] = cls


@defer.inlineCallbacks
def anythingFromId(tid,ds,ready=False):
    tp = yield ds.get("thing:{}:type".format(tid))
    if tp is None:
        raise ThingNotFoundError
    elif not tp in type_to_class:
        raise RuntimeError("no class fitting type {}".format(tp))
    # load it from the datastore and save one db get with pretype
    val = type_to_class[tp](tid,ds=ds,pretype=tp)
    if ready:
        yield val.ready
    defer.returnValue(val)
     
