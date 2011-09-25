"""
module providing access to the bbs
"""
from .data import model
from .data import datasource
from twisted.internet import defer

class BBSService(object):

    def __init__(self,ds):
        self.ds = ds

    def _msg(self,msg,kind="msg"):
        return dict(msg=msg,kind=kind)

    @defer.inlineCallbacks
    def getFrontpage(self):

        try:
            mp = model.Container(6,self.ds)
            yield mp.ready
        except model.ThingNotFoundError:
            defer.returnValue({
                    "msg": self._msg("Couldn't find any content for the front page","error")
                    })
        
        defer.returnValue({
                "main": (yield mp.asDict(contentsParsed=True))
                })

service = BBSService(datasource.getDatasource())
