"""
module providing access to the bbs
"""
from .data import datasource,model
from twisted.internet import defer
from notify import NotificationManager,Notification

class BBSService(object):
    """
    Service providing access to the BBS data
    """
    def __init__(self,ds):
        self.ds = ds
        self._basicInfo = None

        self._notify = NotificationManager()

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
            defer.returnValue({"msg": self._msg("Could not find the requested thing","error")})
            raise
        else:
            defer.returnValue({"thing": (yield thing.asDict(contentsParsed=True))})
            
            
    def _subscribe_to(self,user,thing):
        if hasattr(thing,"add_subscriber"):
            return thing.add_subscriber(user)
    def _unsubscribe(self,user,thing):
        if hasattr(thing,"remove_subscriber"):
            return thing.remove_subscriber(user)


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
        self._subscribe_to(user,cont)
        yield cont.add(post.tid)
        self._notify.add(Notification(cont.subscribers_as_rset(),"new_reply",dict(thing=post,parent=cont)))


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

        topic = model.Topic.new(title,post)
        yield topic.save()


        if user is not None:
            self._subscribe_to(user,topic)

        
        yield cont.add(topic)


        
        
        

service = BBSService(datasource.getDatasource())
