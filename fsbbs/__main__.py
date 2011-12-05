import sys
from fsbbs.mail import EmailInterfaceFactory
from fsbbs.http.application import Application
from twisted.python import log
from twisted.internet import reactor
from fsbbs import config

log.startLogging(sys.stdout)
if config.get("http.enable"):
    smtp = reactor.listenTCP(config.get("email.incoming.port"),EmailInterfaceFactory())
if config.get("email.incoming.enable"):
    http = reactor.listenTCP(config.get("http.port"),Application())
reactor.run()
