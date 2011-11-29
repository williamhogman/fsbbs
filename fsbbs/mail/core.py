from zope.interface import implements
from twisted.internet import defer
from twisted.mail.smtp import SMTPFactory, ESMTP,IMessageDelivery,IMessage,SMTPBadRcpt


class EmailDelivery(object):
    implements(IMessageDelivery)

    def receivedHeader(self,helo,origin,recipients):
        return "Received: EmailDelivery"

    def validateFrom(self, helo, origin):
        # All addresses are accepted
        return origin
    def validateTo(self,user):
        print(user)
        if user.dest.local == "test":
            return lambda: CommandMessage()
        raise  SMTPBadRcpt(user)


class MessageParser(object):
    def __init__(self):
        self.reset()

    def reset(self):
        self.lines = list()
        self.headers =  dict()
        self._in_body = False

    def _add_header(self,header):
        name,val = self._parse_header(header)
        self.headers[name] = val

    def _parse_header(self,header):
        separator = header.find(":")
        name = header[:separator]
        value = header[separator+1:].lstrip()
        return (name,value)

    def feed(self,line):
        # empty line not in body
        if not self._in_body and not line:
            self._in_body = True
        elif self._in_body:
            self.lines.append(line)
        else:
            self._add_header(line)

    def get(self): return (self.headers,self.lines)
    def get_and_reset(self):
        rtn = self.get()
        self.reset()
        return rtn

class ParsedMessage(object):
    def __init__(self):
        self.parser = MessageParser()

    def lineReceived(self,line): self.parser.feed(line)
        
    def eomReceived(self):
        return self.message_parsed(self.parser.get_and_reset())

    def connectionLost(self): self.parser.reset()

class CommandMessage(ParsedMessage):
    implements(IMessage)

    def message_parsed(self,(headers,lines)):
        print(headers)
        print(lines)
        return defer.succeed(None)


    
    
    

class EmailInterfaceFactory(SMTPFactory):
    protocol = ESMTP
    def __init__(self,*a,**kw):
        SMTPFactory.__init__(self,*a,**kw)
        self.delivery = EmailDelivery()
    def buildProtocol(self,addr):
        p = SMTPFactory.buildProtocol(self,addr)
        p.delivery = self.delivery
        return p



