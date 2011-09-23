import cyclone.web
from twisted.internet import defer
from ..service import service
from ..output import json_out,msgpack_out

class IndexHandler(cyclone.web.RequestHandler):
    @defer.inlineCallbacks
    def get(self):
        fp = yield service.getFrontpage()        
        if "msg" in fp:
            self.write(fp['msg']['msg'])

        self.write(str(fp["main"]))



class IndexJsonHandler(cyclone.web.RequestHandler):
    """ gets the index page as JSON """
    @defer.inlineCallbacks
    def get(self):
        fp = yield service.getFrontpage()

        self.write(json_out.serialize(fp))

    
class IndexMsgpackHandler(cyclone.web.RequestHandler):
    """ gets the index page as msgpack """
    @defer.inlineCallbacks
    def get(self):
        fp = yield service.getFrontpage()
        self.write(msgpack_out.serialize(fp))
 

import application

application.addHandlers("index",{"html": IndexHandler, "json": IndexJsonHandler, "msgpack": IndexMsgpackHandler})
