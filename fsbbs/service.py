"""
module providing access to the bbs
"""
from .data import datasource,model
from twisted.internet import defer

class BBSService(object):

    def __init__(self,ds):
        self.ds = ds
        self._basicInfo = None

    def _msg(self,msg,kind="msg"):
        return dict(msg=msg,kind=kind)

    @defer.inlineCallbacks
    def getBasicInfo(self):
        """ gets basic info about a request """
        if self._basicInfo is None:
            mp = model.Forum(6,self.ds)
            yield mp.ready
            self._basicInfo = {"forum": (yield mp.asDict(minimal=True))}

        defer.returnValue(self._basicInfo)


    @defer.inlineCallbacks 
    def getFrontpage(self):
        try:
            mp = model.Forum(6,self.ds)
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
        try:
            thing = yield model.anythingFromId(tid,self.ds,ready=True)
        except model.ThingNotFoundError:
            defer.returnValue({"msg": self._msg("Could not find the requested thing","error")})
            raise
        else:
            defer.returnValue({"thing": (yield thing.asDict(contentsParsed=True))})
            
        

service = BBSService(datasource.getDatasource())
