from zope.interface import implements
from fsbbs.notify.interface import INotificationService
from twisted.plugin import IPlugin
from twisted.python import log
from twisted.internet import defer

class LoggingNM(object):
    """ Basic logging Notification manager """
    implements(IPlugin,INotificationService)
        

    @defer.inlineCallbacks
    def process(self,ntf):
        log.msg("{} with {} to {}".format(
                ntf.kind,
                ntf.obj,
                (yield ntf.recp.get())
                ))
ConsoleLogger = LoggingNM()
