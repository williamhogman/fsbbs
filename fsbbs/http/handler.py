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
        self.formatOutput(data)
            


class JSONDataHandler(BaseDataHandler):
    """ BaseClass for json requests """
    def formatOutput(self,data):
        self.write(json_out.serialize(data))
        

class MsgpackDataHandler(BaseDataHandler):
    """ BaseClass for msgpack requests """
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


