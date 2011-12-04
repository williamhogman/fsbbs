
from twisted.mail.smtp import sendmail
from twisted.internet import defer
from email.message import Message
from fsbbs import config


in_default_domain = lambda user: "{}@{}".format(user,config.get("email.default_domain"))

def clean_addr(addr):
    if "@" in addr:
        return addr # valid
    else:
        return in_default_domain(addr)



class MimeWrap(object):
    def __init__(self,mime,sender,to):
        if isinstance(to,list):
            to = map(clean_addr,to)
        else:
            to =clean_addr(to)
        self.to = to
        self.sender = sender
        self.mime = mime
    def as_mime(self):
        return self.mime
    def send(self):
        _handler.send(self)

    def reply_of(self,msg):
        if "Message-Id" in msg:
            self.add_header("In-Reply-To",msg['Message-Id'])
            refs = msg['Message-Id']
            if "References" in msg:
                refs+=" "+msg['References']
                
            self.add_header("References",refs)
        return self # chaining


class SendmailHandler(object):
    def __init__(self):
        self.smtpserv = config.get("smtp.host")
    @defer.inlineCallbacks
    def send(self,message):
        yield sendmail(self.smtpserv,message.sender,message.to,message.as_mime())
        
        

def _get_handler():
    import sys
    
    return getattr(sys.modules[__name__] ,config.get("smtp.handler")+"Handler")


_Handler = _get_handler()
_handler = _Handler()
