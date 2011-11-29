from zope.interface import implements
from twisted.internet import defer
from parse import ParsedMessage
from twisted.mail.smtp import SMTPFactory, ESMTP,IMessageDelivery,IMessage,SMTPBadRcpt


class EmailDelivery(object):
    """Class for routing emails the correct message class"""
    implements(IMessageDelivery)

    def receivedHeader(self,helo,origin,recipients):
        return "Received: EmailDelivery"

    def validateFrom(self, helo, origin):
        # All addresses are accepted
        return origin
    def validateTo(self,user):
        import post
        if user.dest.local == "test":
            return lambda: CommandMessage()
        elif user.dest.local.startswith("reply-"):
            return lambda: post.Reply()
        elif user.dest.local.startswith("post-"):
            return lambda: post.Post()
        raise  SMTPBadRcpt(user)




class CommandMessage(ParsedMessage):
    implements(IMessage)

    def message_parsed(self,(headers,lines)):
        print(headers)
        print(lines)
        return defer.succeed(None)


    
    
    

class EmailInterfaceFactory(SMTPFactory):
    """ Factory class for the fsbbs smtp server"""
    protocol = ESMTP
    def __init__(self,*a,**kw):
        SMTPFactory.__init__(self,*a,**kw)
        self.delivery = EmailDelivery()
    def buildProtocol(self,addr):
        p = SMTPFactory.buildProtocol(self,addr)
        p.delivery = self.delivery
        return p



