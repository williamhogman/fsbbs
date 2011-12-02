"""
Notifications via email
"""
from twisted.internet import defer
from zope.interface import implements
from interface import INotificationService
from ..data import datasource 
from ..mail import outgoing
from ..a3.user import User

class EmailNotificationService(object):
    implements(INotificationService)
    @defer.inlineCallbacks
    def process(self,notf):
        ds = datasource.getDatasource()
        email_to = notf.recp.intersect(User.with_property(ds,"notify_email"))
        
        body = notf.kind+"\n"+str(notf.obj) # todo: actual templates ;-)

        email_to = yield email_to
        users = yield User.by_ids(email_to,ds)

        for user in users:
            yield user.ready
            if user.email is None:
                continue
            outgoing.NotificationMessage(to=user.email,sender="list",body=body).send()
        
        
        
        
