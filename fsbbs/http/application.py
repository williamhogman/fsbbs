import os
import sys
import cyclone.web
import cyclone.httpclient
from twisted.python import log
from twisted.internet import defer, reactor

from .index import IndexHandler
#from .things import ThingHandler

class Application(cyclone.web.Application):
    def __init__(self):
        handlers = [
            (r"/", IndexHandler),
#            (r"/([^/]+)/([^/]+)\.html",ThingHandler),
        ]
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            autoescape="xhtml_escape",
        )
        cyclone.web.Application.__init__(self, handlers, **settings)
