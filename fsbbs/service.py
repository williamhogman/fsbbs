"""
module providing access to the bbs
"""
import json

from .data import datasource,model
from twisted.internet import defer
from twisted.python import log


class BBSService(object):
    """
    Service providing access to the BBS data
    """
    def __init__(self,ds):
        self.ds = ds
        self._basicInfo = None

    def _msg(self,msg,kind="msg"):
        return dict(msg=msg,kind=kind)

    @defer.inlineCallbacks
    def getBasicInfo(self):
        """ gets basic information about the hosted forum"""
        if self._basicInfo is None:
            mp = model.Forum(1,self.ds)
            yield mp.ready
            self._basicInfo = {"forum": (yield mp.asDict(minimal=True))}

        defer.returnValue(self._basicInfo)


    @defer.inlineCallbacks 
    def getFrontpage(self):
        """
        Gets the frontpage
        """
        try:
            mp = model.Forum(1,self.ds)
            yield mp.ready
        except model.ThingNotFoundError:
            defer.returnValue({
                    "msg": self._msg("Couldn't find any content for the front page","error")
                    })
        else:
            defer.returnValue({
                    "main": (yield mp.asDict(contentsParsed=True))
                    })

    @defer.inlineCallbacks
    def getThing(self,tid,throw=False):
        """ 
        Gets a thing from the database'
        """
        try:
            thing = yield model.anythingFromId(tid,self.ds,ready=True)
        except model.ThingNotFoundError:
            # honour throw: returnValue raises, so the re-raise has to come first
            if throw:
                raise
            defer.returnValue({"msg": self._msg("Could not find the requested thing","error")})

        else:
            defer.returnValue({"thing": (yield thing.asDict(contentsParsed=True))})
            
    def _publish(self,tid,event):
        """ fires a realtime event on the channel of a thing, failures are non fatal """
        d = self.ds.publish("fsbbs:thing:{}".format(tid),json.dumps(event))
        d.addErrback(lambda f: log.msg("could not publish event: {}".format(f.value)))
        return d

    @defer.inlineCallbacks
    def postToThing(self,tid,text,user):
        """
        Create a post inside a thing
        """
        cont = yield model.anythingFromId(tid,self.ds,ready=True)
        post = model.Post.new(text,user.uid,ds=self.ds)
        if not hasattr(cont,"add"):
            raise RuntimeError("could not add post to {}".format(cont.__class__.__name__))

        yield post.save()
        yield cont.add(post.tid)
        self._publish(tid,{"event": "post", "tid": post.tid, "parent": int(tid)})
        defer.returnValue(post.tid)

    @defer.inlineCallbacks
    def newTopic(self,tid,title,text,user=None):
        """
        Creates a new topic in a thing
        """
        cont = yield model.anythingFromId(tid,self.ds,ready=True)

        if not hasattr(cont,"add"):
            raise RuntimeError("could not create topic in {}".format(cont.__class__.__name__))

        post = model.Post.new(text,user.uid,ds=self.ds)
        yield post.save()

        topic = model.Topic.new(title,post,ds=self.ds)
        yield topic.save()
        
        yield cont.add(topic.tid)
        self._publish(tid,{"event": "topic", "tid": topic.tid, "parent": int(tid),
                           "title": title})
        defer.returnValue(topic.tid)

    @defer.inlineCallbacks
    def vote(self,tid,uid,delta):
        """
        Casts a single vote on a thing. Votes are one per user and they rescore
        the thing inside its parent container, which is what orders listings.
        """
        delta = 1 if int(delta) >= 0 else -1
        tid = int(tid)

        # raises ThingNotFoundError for made up ids
        yield model.anythingFromId(tid,self.ds,ready=True)

        first = yield self.ds.setnx("vote:{}:{}".format(tid,uid),delta)
        if not first:
            score = yield self.ds.get("thing:{}:score".format(tid))
            defer.returnValue({"status": "already_voted", "score": int(score or 0)})

        score = yield self.ds.incr("thing:{}:score".format(tid),delta)
        parent = yield self.ds.get("thing:{}:parent".format(tid))
        if parent is not None:
            yield self.ds.zincrby("thing:{}:contents".format(parent),delta,tid)
            self._publish(parent,{"event": "vote", "tid": tid, "parent": int(parent),
                                  "score": int(score)})

        defer.returnValue({"status": "success", "score": int(score), "tid": tid})



        
        
        

service = BBSService(datasource.getDatasource())
