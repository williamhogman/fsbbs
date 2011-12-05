import sys
from twisted.internet import defer
from twisted.python import log
from twisted.plugin import getPlugins
from fsbbs.notify.interface import INotificationService

class Notification(object):
    """ A notification """
    def __init__(self,recp,kind,obj):
        self.recp = recp
        self.kind = kind
        self.obj = obj


class NotificationManager(object):
    """ Manages the sending of notifications."""
    def __init__(self):
        self.managers = list()
        import fsbbs.plugins.notify as plugins
        mgrs = getPlugins(INotificationService,plugins)
        self.managers += mgrs
        import email
        em = email.EmailNotificationService()
        self.managers.append(em)
        import im
        n = im.IMNotificationService()
        self.managers.append(n)

    @defer.inlineCallbacks
    def add(self,notf):
        """Adds a notification into the notification system"""
        defs = list()
        for manager in self.managers:
            defs.append(manager.process(notf))
        yield defer.DeferredList(defs)
        
        
        

