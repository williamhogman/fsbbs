"""
Core components in the incoming mail system
"""

from zope.interface import implements
from twisted.mail.smtp import SMTPFactory, ESMTP, IMessageDelivery
from twisted.mail.smtp import SMTPBadRcpt

from fsbbs.mail import post


class EmailDelivery(object):
    """Class for routing emails the correct message class"""
    implements(IMessageDelivery)

    def receivedHeader(self, helo, origin, recipients):
        """ Adds our Received header """
        return "Received: EmailDelivery"

    def validateFrom(self, helo, origin):
        """ 
        validates origins, for now we don't do any verification,
        use a proxy for that return origin
        """
        return True

    def validateTo(self, user):
        """ validates the incoming addresses """
        if user.dest.local.startswith("reply-"):
            return lambda: post.Reply(user.dest.local)
        elif user.dest.local.startswith("post-"):
            return lambda: post.Post(user.dest.local)
        raise  SMTPBadRcpt(user)



class EmailInterfaceFactory(SMTPFactory):
    """ Factory class for the fsbbs smtp server"""
    protocol = ESMTP
    def __init__(self, *a, **kw):
        SMTPFactory.__init__(self, *a, **kw)
        self.delivery = EmailDelivery()

    def buildProtocol(self, addr):
        proto = SMTPFactory.buildProtocol(self, addr)
        proto.delivery = self.delivery
        return proto



