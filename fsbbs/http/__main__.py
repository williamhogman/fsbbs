from twisted.internet import defer, reactor
from twisted.python import log
from .application import Application
import sys

log.startLogging(sys.stdout)
app = Application()
reactor.listenTCP(3037, app)
reactor.run()
