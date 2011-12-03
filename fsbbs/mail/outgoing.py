
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

class OutgoingMessage(object):
    @classmethod
    def reply_to(cls,msg,*args,**kwargs):
        inst = cls(to=msg['From'],*args,**kwargs)
        print(msg)
        if "Message-Id" in msg:
            inst.add_header("In-Reply-To",msg['Message-Id'])

            refs = msg['Message-Id']
            if "References" in msg:
                refs+=" "+msg['References']
                
            inst.add_header("References",refs)
        return inst

    def add_header(self,name,val):
        self.headers[name] = val
    def __init__(self,sender=None,to=None,body=None,subject=None):
        self.sender = sender
        if isinstance(to,list):
            to = map(clean_addr,to)
        else:
            to = clean_addr(to)

        self.to = to 
        self.body =body
        self.headers = dict()
        if subject is not None:
            self.headers["Subject"] = subject
    def send(self):
        _handler.send(self)
    def as_mime(self):
        msg = Message()
        msg['To'] = self.to
        msg['From'] = self.sender
        msg.set_payload(self.body,"utf-8")
        for k,v in self.headers.iteritems():
            msg[k] = v

        return msg
        

class ErrorMessage(OutgoingMessage):
    def __init__(self,sender=None,*args,**kwargs):
        if not sender:
            sender = in_default_domain("error")
        OutgoingMessage.__init__(self,sender=sender,*args,**kwargs)


class AuthFailedMessage(ErrorMessage):
    def __init__(self,body=None,subject=None,*args,**kwargs):
        if not body:
            body = "We were unable to verify your identity."
        if not subject:
            subject = "ERROR - Authentication failed"
        ErrorMessage.__init__(self,body=body,
                              subject=subject,
                              *args,**kwargs)
    


class NotificationMessage(OutgoingMessage):
    """ A message that notifies a user of something, where no action is required"""
    def __init__(self,sender=None,*args,**kwargs):
        if not sender:
            sender = in_default_domain("noreply")
        OutgoingMessage.__init__(self,sender=sender,*args,**kwargs)

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
