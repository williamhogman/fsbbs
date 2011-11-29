from  .core import EmailInterfaceFactory
from twisted.python import log
from twisted.internet import reactor
import sys

log.startLogging(sys.stdout)
serv = reactor.listenTCP(2500,EmailInterfaceFactory())
reactor.run()














