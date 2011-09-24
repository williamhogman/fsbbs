import cyclone.web
from .handler import BaseHandler,SimpleJSON,SimpleMsgpack,SessionAuthMixin
from twisted.internet import defer
from ..service import service
from ..output import json_out,msgpack_out

class IndexHandler(BaseHandler,SessionAuthMixin):
    @defer.inlineCallbacks
    def get(self):
        ses_ver = self.verifySession()
        
        fp = yield service.getFrontpage()
        
        if (yield ses_ver):
            self.write("welcome back")
        if "msg" in fp:
            self.write(fp['msg']['msg'])

        self.write(str(fp["main"]))


import application

application.addHandlers("index",{"html": IndexHandler, "json": SimpleJSON(service.getFrontpage), "msgpack": SimpleMsgpack(service.getFrontpage)})
