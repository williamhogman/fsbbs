import os
import sys
import cyclone.web
import cyclone.httpclient
from twisted.python import log
from twisted.internet import defer, reactor


#from .things import ThingHandler


_handlers = list()

def addHandler(path,handler):
    """ 
    adds a handler to the list of handlers to be added doesn't work affect instances of
    application that have already been instansiated
    """
    _handlers.append((path,handler))

def addHandlers(path,subhandlers):
    """ adds more than one handlers sharing an extensions such as index.html, index.json and so on """
    for ext,handler in subhandlers.iteritems():
        addHandler("/{}.{}".format(path,ext), handler)




import index
import thing
import auth



class Application(cyclone.web.Application):
    def __init__(self):
        handlers = _handlers

        settings = dict(
        )
        handlers.append((r"/s/(.*)",cyclone.web.StaticFileHandler,{"path": "themes/default/static/"}))
        handlers.append((r"/j/(.*)",cyclone.web.StaticFileHandler,{"path": "javascript/" }))
        cyclone.web.Application.__init__(self, handlers, **settings)
