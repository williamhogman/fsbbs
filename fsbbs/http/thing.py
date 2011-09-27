import cyclone.web
from .handler import BaseHandler,SimpleJSON,SimpleMsgpack,SessionAuthMixin,JSONDataHandler
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
            upd = {"user": self.user, "logged_in":self.logged_in} if (yield ses_ver) else {"logged_in": self.logged_in}
            thing.update(upd)
            thing.update((yield service.getBasicInfo()))
            html.OutputFormatter.dump("thing.html",thing,self)
        

class ThingJSONHandler(JSONDataHandler):
    @defer.inlineCallbacks
    def getData(self):
        tid = self.get_argument("id")
        try:
            thing = yield service.getThing(tid,throw=True)
        except ThingNotFoundError:
            self.set_status(404)
        else:
            defer.returnValue(thing)
            
import application
application.addHandler(r"/t/([1-9]+).html",ThingHandler)
application.addHandler(r"/api/get_thing.json",ThingJSONHandler)
