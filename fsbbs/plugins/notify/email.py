"""
Notifications via email
"""
from twisted.internet import defer
from twisted.plugin import IPlugin
from zope.interface import implements
from fsbbs.notify.interface import INotificationService
from fsbbs.data import datasource 
from fsbbs.mail import outgoing
from fsbbs.a3.user import User
from fsbbs.output import mail


class EmailNotificationService(object):
    """ Email notifier """
    implements(IPlugin,INotificationService)
    @defer.inlineCallbacks
    def process(self,notf):
        ds = datasource.getDatasource()
        email_to = notf.recp.intersect(User.with_property(ds,"notify_email"))
        
        message = yield mail.Output.render_message(notf.kind,notf.obj)
        sender = message['From']
        start = sender.find("<") +1
        if start:
            sender = sender[start:sender[start].find(">")]
        
            
        email_to = yield email_to
        users = yield User.by_ids(email_to,ds)
        
        for user in users:
            yield user.ready


            if user.email is None:
                continue
            outgoing.MimeWrap(message,sender,user.email).send()

ems = EmailNotificationService()
