"""
Notifications via email
"""
from twisted.internet import defer
from twisted.python import log
from zope.interface import implements
from interface import INotificationService
from ..data import datasource 
from ..mail import outgoing
from ..a3.user import User
from fsbbs.output import mail

class EmailNotificationService(object):
    implements(INotificationService)
    @defer.inlineCallbacks
    def process(self,notf):
        ds = datasource.getDatasource()
        log.msg("email notif")
        email_to = notf.recp.intersect(User.with_property(ds,"notify_email"))
        
        body = self.__build_body(notf)

        email_to = yield email_to
        users = yield User.by_ids(email_to,ds)

        for user in users:
            yield user.ready


            if user.email is None:
                continue
            outgoing.NotificationMessage(to=user.email,sender="list",body=body).send()


        
        
        
        
    def __build_body(self,notf):
        return mail.Output.render_plain_body(notf.kind,notf.obj)
