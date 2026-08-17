import os
import sys

from twisted.internet import defer, reactor
from twisted.python import log

from .application import Application

log.startLogging(sys.stdout)
app = Application()
port = int(os.environ.get("PORT", "3037"))
log.msg("fsbbs listening on port {}".format(port))
reactor.listenTCP(port, app)
reactor.run()
