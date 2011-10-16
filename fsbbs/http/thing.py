import cyclone.web
from .handler import BaseHandler,SimpleJSON,SimpleMsgpack,SessionAuthMixin,JSONDataHandler
from twisted.internet import defer
from ..service import service
from ..output import json_out,msgpack_out,html
from ..data.model import ThingNotFoundError

class ThingHandler(BaseHandler,SessionAuthMixin):
    """handler for thing pages"""
    @defer.inlineCallbacks
    def get(self,tid):
        ses_ver = self.verifySession()
        try:
            thing = yield service.getThing(tid,throw=True)
        except ThingNotFoundError:
            
            self.set_status(404)
            self.write("404")
        else:
            yield ses_ver
            thing.update(self.getUserDict())
            thing.update((yield service.getBasicInfo()))
            html.OutputFormatter.dump("thing.html",thing,self)
        

class ThingJSONHandler(JSONDataHandler):
    """ provides a method callable via JSON+XHR that returns the passed in thing"""
    @defer.inlineCallbacks
    def getData(self):
        tid = self.get_argument("id")
        try:
            thing = yield service.getThing(tid,throw=True)
        except ThingNotFoundError:
            self.set_status(404)
        else:
            defer.returnValue(thing)


class PostToContainer(BaseHandler,SessionAuthMixin):
    """ handler for posting to any container"""
    @defer.inlineCallbacks
    def post(self):
        yield self.verifySession()
        
        if not self.requireLogin():
            return
        tid = int(self.get_argument("tid"))
        text = self.get_argument("text")      
        yield service.postToThing(tid,text,self.user)
        self.redirect("/t/{}.html".format(tid))
        
class NewTopic(BaseHandler,SessionAuthMixin):
    """ handler for posting new topics"""
    @defer.inlineCallbacks
    def post(self):
        yield self.verifySession()
        
        if not self.requireLogin():
            return
        
        tid = int(self.get_argument("tid"))
        title = self.get_argument("title")
        text = self.get_argument("text")
        
        yield service.newTopic(tid,title,text,self.user)
        
        self.redirect("/t/{}.html".format(tid))


            
import application
application.addHandler(r"/t/([1-9]+).html",ThingHandler)
application.addHandler(r"/api/get_thing.json",ThingJSONHandler)
application.addHandler(r"/new_post",PostToContainer)
application.addHandler(r"/new_topic",NewTopic)
