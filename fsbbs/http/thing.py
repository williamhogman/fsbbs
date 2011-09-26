import cyclone.web
from .handler import BaseHandler,SimpleJSON,SimpleMsgpack,SessionAuthMixin
from twisted.internet import defer
from ..service import service
from ..output import json_out,msgpack_out,html
from ..data.model import ThingNotFoundError

class ThingHandler(BaseHandler,SessionAuthMixin):
    @defer.inlineCallbacks
    def get(self,tid):
        ses_ver = self.verifySession()
        try:
            thing = yield service.getThing(tid,throw=True)
        except ThingNotFoundError:
            
            self.set_status(404)
            self.write("404")
        else:
            thing.update((yield service.getBasicInfo()))
            html.OutputFormatter.dump("thing.html",thing,self)
        
            
            
            
import application
application.addHandler(r"/t/([1-9]+).html",ThingHandler)
