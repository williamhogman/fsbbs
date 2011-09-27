import cyclone.web
from .handler import BaseHandler,SimpleJSON,SimpleMsgpack,SessionAuthMixin
from twisted.internet import defer
from ..service import service
from ..output import json_out,msgpack_out,html
from ..a3 import AuthService

class LoginHandler(BaseHandler,SessionAuthMixin):
    @defer.inlineCallbacks
    def get(self):
        logged_in = yield self.verifySession()
        if logged_in:
            self.redirect("/index.html")
            return
        dt = yield service.getBasicInfo()
        dt.update(dict(logged_in=False))
        html.OutputFormatter.dump("login.html",dt,self)
            
    @defer.inlineCallbacks
    def post(self):
        username = self.get_argument("username")
        password = self.get_argument("password")
        auth = AuthService()
        res = yield auth.getChain("default").run({"username": username,"password": password})

        if res.success:
            # if we've been asked to store a secret
            if 'set_session_secret' in res:
                self.set_cookie("s",res['set_session_secret'])
            self.redirect("/index.html")
        else:
            
            auth = {"logged_in": False, "msg": {"kind": "error", "msg": "Login failed"}}
            auth.update((yield service.getBasicInfo()))
            html.OutputFormatter.dump("login.html",
                                      auth,
                                      self)
        

class LogoutHandler(BaseHandler):
    
    def get(self):
        self.clear_cookie("s")
        self.redirect("/index.html")
        
import application
application.addHandler(r"/login.html",LoginHandler)
application.addHandler(r"/logout.html",LogoutHandler)
