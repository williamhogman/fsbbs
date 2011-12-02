from twisted.internet import defer

class Notification(object):
    """ A notification """
    def __init__(self,recp,kind,obj):
        self.recp = recp
        self.kind = kind
        self.obj = obj

notificationManagers = dict()

class ConsoleNM(object):
    @defer.inlineCallbacks
    def process(self,ntf):
        print("{} with {} to {}".format(
                ntf.kind,
                ntf.obj,
                (yield ntf.recp.get())
                ))


class NotificationManager(object):
    """ Manages the sending of notifications."""
    def __init__(self):
        self.managers = list()
        self.managers.append(ConsoleNM())

    @defer.inlineCallbacks
    def add(self,notf):
        """Adds a notification into the notification system"""
        defs = list()
        for manager in self.managers:
            defs.append(manager.process(notf))
        yield defer.DeferredList(defs)
        
        
        

