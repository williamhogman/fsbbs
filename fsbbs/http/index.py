import cyclone.web
from .handler import BaseHandler,SimpleJSON,SimpleMsgpack,SessionAuthMixin
from twisted.internet import defer
from ..service import service
from ..output import json_out,msgpack_out,html


class IndexHandler(BaseHandler,SessionAuthMixin):
    @defer.inlineCallbacks
    def get(self):
        ses_ver = self.verifySession()

        fp = yield service.getFrontpage()
        upd = {"user": self.user, "logged_in":self.logged_in} if (yield ses_ver) else {"user": self.logged_in}
        fp.update(upd)    
        html.OutputFormatter.dump("index.html",fp,self)
        
        


import application

application.addHandlers("index",{"html": IndexHandler, "json": SimpleJSON(service.getFrontpage), "msgpack": SimpleMsgpack(service.getFrontpage)})
