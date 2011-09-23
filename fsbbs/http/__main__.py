from twisted.internet import defer, reactor
from .application import Application

app = Application()
reactor.listenTCP(8888, app)
reactor.run()
