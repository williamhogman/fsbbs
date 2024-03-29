"""
Module for http handlers involved in authentication.
"""
from .handler import BaseHandler, SessionAuthMixin
from twisted.internet import defer
from ..service import service
from ..output import json_out, html
from ..a3 import AuthService

class LoginHandler(BaseHandler, SessionAuthMixin):
    """provides a login form"""
    @defer.inlineCallbacks
    def get(self):
        logged_in = yield self.verifySession()
        if logged_in:
            self.redirect("/index.html")
            return
        data = yield service.getBasicInfo()
        html.OutputFormatter.dump("login.html", data, self)
            
    @defer.inlineCallbacks
    def post(self):
        logged_in = yield self.verifySession()
        if logged_in:
            self.redirect("/index.html")
            return

        username = self.get_argument("username")
        password = self.get_argument("password")
        auth = AuthService()
        res = yield auth.getChain("default").run({"username": username,
                                                  "password": password})

        if res.success:
            # if we've been asked to store a secret
            if 'set_session_secret' in res:
                self.set_cookie("s", res['set_session_secret'])
            self.redirect("/index.html")
        else:
            auth = {"logged_in": False, "msg": {"kind": "error",
                                                "msg": "Login failed"}}
            auth.update((yield service.getBasicInfo()))
            html.OutputFormatter.dump("login.html",
                                      auth,
                                      self)
        




class RegisterHandler(BaseHandler, SessionAuthMixin):
    """ provides a register form """
    @defer.inlineCallbacks
    def get(self):
        logged_in = yield self.verifySession()
        if logged_in:
            self.redirect("/index.html")
            return
        data = yield service.getBasicInfo()
        html.OutputFormatter.dump("register.html", data, self)
    @defer.inlineCallbacks
    def post(self):
        logged_in = yield self.verifySession()
        if logged_in:
            self.redirect("/index.html")
            return
        username = self.get_argument("username")
        password = self.get_argument("password")
        auth = AuthService()  
        res = yield auth.getChain("register").run({"username":username,
                                                   "new_password": password})
        if res.success:
            if 'set_session_secret' in res:
                self.set_cookie("s", res['set_session_secret'])
            data = dict()
            data.update((yield service.getBasicInfo()))
            data['new_username'] = username.lower()
            data['hidelogin'] = True
            html.OutputFormatter.dump("new_user.html", data, self)
        else:
            data = {"msg": {"msg": "Could not register user", "kind": "error"}}
            data.update((yield service.getBasicInfo()))
            html.OutputFormatter.dump("register.html", data, self)


class LogoutHandler(BaseHandler):
    """ provides a handler for logging out and redirects the user"""
    def get(self):
        self.clear_cookie("s")
        #todo: invalidate the login cookie
        self.redirect("/index.html")

from ..output import json_out

class RegisterJSONHandler(BaseHandler, SessionAuthMixin):
    """
    provides a registration method callable via JSON+XHR
    """
    @defer.inlineCallbacks
    def post(self):
        logged_in = yield self.verifySession()
        if logged_in:
            self.finish(json_out.serialize({"status": "invalid",
                                            "uid": self.user.uid}))
            return
        
        username = self.get_argument("username")
        password = self.get_argument("password")
        
        auth = AuthService()
        res = yield auth.getChain("register").run({"username": username,
                                                   "new_password": password})

        self.set_header("Content-Type","application/json")
        if res.success:
            if 'set_session_secret' in res:
                self.set_cookie("s", res['set_session_secret'])

            self.finish(json_out.serialize({"status": "success",
                                            "uid": res.uid,
                                            "username": username.lower()}))
        else:
            self.finish(json_out.serialize({"status": "failure"}))
            return
                        
        

class LoginJSONHandler(BaseHandler, SessionAuthMixin):
    """
    provides a login method callable via JSON+XHR
    """
    @defer.inlineCallbacks
    def post(self):
        logged_in = yield self.verifySession()
        if logged_in:
            self.finish(json_out.serialize({"status": "invalid",
                                            "uid": self.user.uid}))
            return
        username = self.get_argument("username")
        password = self.get_argument("password")
        auth = AuthService()
        res = yield auth.getChain("default").run({"username": username,
                                                  "password": password})

        self.set_header("Content-Type", "application/json")
        if res.success:
            # if we've been asked to store a secret
            if 'set_session_secret' in res:
                self.set_cookie("s", res['set_session_secret'])

            self.finish(json_out.serialize({"status": "success",
                                            "msg": "Logged in",
                                            "uid": res.uid}))
        else:
            self.finish(json_out.serialize({"status": "failure",
                                            "msg": "Incorrect credentials"}))
        
            

class LogoutJSONHandler(BaseHandler):
    """
    provides a logout method callable via JSON+XHR
    """
    def post(self):
        self.clear_cookie("s")
        self.set_header("Content-Type","application/json")
        #todo: invalidate the actual cookie
        self.finish(json_out.serialize({"success": True}))
        
import application

application.addHandler(r"/api/logout.json", LogoutJSONHandler)
application.addHandler(r"/api/login.json", LoginJSONHandler)
application.addHandler(r"/api/register.json", RegisterJSONHandler)
application.addHandler(r"/login.html", LoginHandler)
application.addHandler(r"/logout.html", LogoutHandler)
application.addHandler(r"/register.html", RegisterHandler)
