"""
functions and classes modifying the standard cyclone.web.handler
"""
import cyclone.web
from twisted.internet import defer
from ..output import json_out,msgpack_out

class BaseHandler(cyclone.web.RequestHandler):
    """ 
    all fsbbs requests handlers are derived from this class,
    doesn't override any cyclone behaviour yet
    """


class BaseDataHandler(BaseHandler):
    mimetype = "application/octet-stream"
    """ Class for an HTTP request returning data thru a output handler """
    def getData(self):
        """
        when overridden in a derived class returns a deferred which if 
        successfull calls back with the data needed for the request
        """

    def formatOutput(self,data):
        """
        when overriden in a derived class formats the output into a format (e.g. HTML)
        and outputs it to the response
        """

    @defer.inlineCallbacks
    def get(self):
        data = yield self.getData()
        self.set_header("Content-Type",self.mimetype)
        self.formatOutput(data)
            


class JSONDataHandler(BaseDataHandler):
    mimetype = "application/json"
    """ BaseClass for json requests """
    def formatOutput(self,data):
        self.write(json_out.serialize(data))
        

class MsgpackDataHandler(BaseDataHandler):
    """ BaseClass for msgpack requests """

    # actually there is no specified mime type for msgpack
    # the consensus seems to be to use x-msgpack this may change
    mimetype = "application/x-msgpack"
    def formatOutput(self,data):
        self.write(msgpack_out.serialize(data))


class SimpleMsgpackHandler(MsgpackDataHandler):

    @defer.inlineCallbacks
    def getData(self):
        data = yield self.data_function()
        defer.returnValue(data)

    def __init__(self,data_function,app,request):
        self.data_function = data_function
        super(SimpleMsgpackHandler,self).__init__(app,request)


class SimpleJSONHandler(JSONDataHandler):
    @defer.inlineCallbacks
    def getData(self):
        data = yield self.data_function()
        defer.returnValue(data)

    def __init__(self,data_function,app,request):
        # this shouldn't bind the function
        self.data_function = data_function
        super(SimpleJSONHandler,self).__init__(app,request)


def SimpleJSON(data_function):
    def inner(app,request):
        return SimpleJSONHandler(data_function,app,request)
    return inner

def SimpleMsgpack(data_function):
    def inner(app,request):
        return SimpleMsgpackHandler(data_function,app,request)
    return inner


from ..a3 import AuthService
from ..a3.user import User
from ..data import datasource
class SessionAuthMixin(object):
    """ mixin adding funcionality for easily verifying sessions """
    @defer.inlineCallbacks
    def verifySession(self):
        authserv = AuthService()
        session_cookie = self.get_cookie("s")
        if session_cookie is None:
            self.logged_in = False
            defer.returnValue(False)
        res = yield authserv.getChain("session").run({"session_secret": session_cookie})

        self.logged_in = res.success
        if self.logged_in:
            self.user = User(res.uid,datasource.getDatasource())
            yield self.user.ready

        defer.returnValue(res.success)
            

            
            
        
