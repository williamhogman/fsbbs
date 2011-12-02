import datetime
import time

from twisted.internet import defer
from twisted.python import log

from thing import Thing
from types import RSet

class ThingNotFoundError(RuntimeError):
    """ error to be raised when a thing cannot be found """



class SubscriptionMixin(object):
    """ Mixin providing an interface for subscribing"""

    def __uid(self,user):
        return user.uid if hasattr(user,"uid") else int(user)
        

    def is_subscriber(self,user):
        """ 
        determines if the passed in user is a subscriber. returns a
        defered returning true or false
        """
        uid = self.__uid(user)
        return self.datasource.sismember(self._key("subscribers"),uid)
    def add_subscriber(self,user):
        """ adds a user as a subscriber to this thing """
        uid = self.__uid(user)
        return self.datasource.sadd(self._key("subscribers"),uid)

    def remove_subscriber(self,user):
        """remove a subscriber """
        uid = self.__uid(user)
        return self.datasource.srem(self._key("subscribers"),uid)

    def get_subscribers(self):
        """ 
        gets all subscribers, O(N) where N is the number of
        memebers in the set. and N can get big in a large thread
        """
        return self.datasource.smembers(self._key("subscribers"))

    def subscribers_as_rset(self):
        return RSet(self._key("subscribers"),self.datasource)
        

class Container(Thing):
    """ A thing containing a sorted set of other things"""
    def __init__(self,tid,*args,**kwargs):
        super(Container,self).__init__(tid,*args,**kwargs)
        @defer.inlineCallbacks
        def onReady(a):
            self.contents = yield self.datasource.zrange(self._key("contents"))
        if tid > 0:
            self.ready.addCallback(onReady)
        
    @defer.inlineCallbacks
    def add(self,thing,score=0):
        # convert to tid
        if hasattr(thing,"tid"):
            tid = thing.tid
        else:
            tid = int(thing)
        """ adds a pointer to the passed in thing this operation does not wait for save"""
        self.contents.append(thing)
        yield self.datasource.zadd(self._key("contents"),score,tid)
    def get_contents(self):
        """gets the contents of the container"""
        return manyFromIds(self.contents,self.datasource,ready=True)
        defs = list()
        for tid in self.contents:
            ## yo dawg so i herd u liek async!
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
                    
                
    @defer.inlineCallbacks
    def _contentsAsDict(self):
        things = yield self.get_contents()

        ret = list()
        for t in things:
            ret.append((yield t.asDict()))

        defer.returnValue(ret)


    @defer.inlineCallbacks
    def asDict(self,bs=None,contentsParsed=False,**kwargs):
        """gets the container as a dict suitable for serialization"""
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

class Topic(Container,SubscriptionMixin):
    """ A topic is a list of post with one original post and poster"""
    def __init__(self,tid,*args,**kwargs):
        super(Topic,self).__init__(tid,*args,**kwargs)
        @defer.inlineCallbacks
        def onReady(a):
            # the original post that started the topic
            self.original_post,self.title = yield self._mget("original_post","title")

        if tid>0:
            self.ready.addCallback(onReady)
        

    @defer.inlineCallbacks
    def asDict(self,bs=None,**kwargs):
        """gets the topic as a dict"""
        d = {"title": self.title}
        try:
            op = yield anythingFromId(self.original_post,self.datasource,ready=True)
            op_dict= yield op.asDict()
        except ThingNotFoundError:
            log.msg("Could not find OP in {}".format(self.tid)) # if we can't find the OP just go on
        else:
            d.update({"original_post": op_dict})

        s = yield super(Topic,self).asDict(bs=d,**kwargs)
        d.update(s)
        if bs is None:
            defer.returnValue(d)
        else:
            bs.update(d)
            defer.returnValue(bs)


    

    @staticmethod
    def new(title,original_post,ds=None):
        """ creates a new topic (as opposed to just an representation of a preexisting one """
        t = Topic(-1,ds)
        t.original_post = original_post.tid
        t.title = title
        return t

    @defer.inlineCallbacks
    def save(self):
        """ saves the topic to the datastore """
        if not self.update:
            yield self.newThing("topic")
            self.update = True
        yield self._set("original_post",self.original_post)
        yield self._set("title", self.title)
            


class Post(Thing):
    """ A post """
    def __init__(self,tid,*args,**kwargs):
        super(Post,self).__init__(tid,*args,**kwargs)
        @defer.inlineCallbacks
        def onReady(a):
            self.poster_uid, self.text,self.pubdate_stamp= yield self._mget("poster_uid","text","pubdate")
            self.poster_name = yield usernameById(self.poster_uid,self.datasource)
            #yield self.datasource.get("user:{}:username".format(self.poster_uid))

        if tid > 0:
            self.ready.addCallback(onReady)
    
    @property
    def pubdate(self):
        """Gets the pubdate as a pythondate"""
        if self.pubdate_stamp is None:
            return None
        return datetime.datetime.utcfromtimestamp(self.pubdate_stamp)
    @pubdate.setter
    def pubdate(self,value):
        self.pubdate_stamp = time.mktime(value.timetuple())

    @defer.inlineCallbacks
    def save(self):
        """saves a post to datastore"""
        if not self.update:
            yield self.newThing("post")
            self.update = True
        self._set('poster_uid',self.poster_uid)
        self._set('text',self.text) 
        self._set("pubdate",self.pubdate_stamp)
        
    @staticmethod
    def new(text,uid,pubdate=None,ds=None):
        """ creates a new post """
        p = Post(-1,ds)

        p.poster_uid = uid
        p.text = text
        if pubdate is None:
            p.pubdate_stamp = time.time()
        else:
            p.pubdate_stamp = pubdate

        return p

        


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
    def __init__(self,tid,*args,**kwargs):
        super(Category,self).__init__(tid,*args,**kwargs)
        @defer.inlineCallbacks
        def onReady(a):
            self.title,self.description = yield self._mget("title","description")
        if tid>0:
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
    def __init__(self,tid,*args,**kwargs):
        super(Forum,self).__init__(tid,*args,**kwargs)
        @defer.inlineCallbacks
        def onReady(a):
            self.name,self.tagline = yield self._mget("name","tagline")
        if tid>0:
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



# dict containing our type name to class mapping
type_to_class = {}

# creating a mapping list between types in the db and our classes
for cls in [Container,Topic,Post,Forum,Category]:
    type_to_class[cls.__name__.lower()] = cls

user_cache = dict()
@defer.inlineCallbacks
def usernameById(userid,ds):
    """ 
    caching function getting a username by user id
    TODO: move this deeper into the datalayer
    """
    if userid in user_cache:
        defer.returnValue(user_cache[userid])
    else:
        user_cache[userid] = username = yield ds.get("user:{}:username".format(userid))
        defer.returnValue(username)
    
    
@defer.inlineCallbacks
def manyFromIds(tids,ds,ready=False,throw=False):
    """ returns a list of things when passed in a list of tids """

    # one or fewer are special cases
    if len(tids) < 2:

        if len(tids) > 0:
            # just call the simpler function
            thing = yield anythingFromId(tids[0],ds,ready=ready)
            defer.returnValue([thing])
        else:
            # return an empty list
            defer.returnValue(list())

    def tidsToKey(tids):
        for t in tids:
            yield "thing:"+str(t)+":type"
        
    things = list()
    # pass in tids to the function
    types = yield ds.mget(*tidsToKey(tids))
 

    for i in xrange(len(tids)):
        if types[i] is None:
            if throw:
                raise ThingNotFoundError
            else:
                log.msg("Thing {} not found".format(tids[i]))
                continue
        elif not types[i] in type_to_class:
            raise RuntimeError("no class fitting type {}".format(tp))
        
        things.append(type_to_class[types[i]](tids[i],ds=ds,pretype=types[i]))
        
    # we wait for readyness once all the things have been loaded
    if ready:
        # get a list of things  and make a defered
        yield defer.DeferredList([thing.ready for thing in things])
    
    defer.returnValue(things)
    
    

@defer.inlineCallbacks
def anythingFromId(tid,ds,ready=False):
    """ returns a subclass of the thing by tid"""
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
     
