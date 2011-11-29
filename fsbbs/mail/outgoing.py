from .. import config

class OutgoingMessage(object):
    def send(self):
        print(self)

class ErrorMessage(OutgoingMessage):
    def __init__(self,msg):
        self.msg = msg


class SendmailHandler(object):
    def __init__(self):
        self.hostname = config.get("smtp.host")
    def send(self,message):
        pass
        

def _get_handler():
    import sys
    
    return getattr(sys.modules[__name__] ,config.get("smtp.handler")+"Handler")


Handler = _get_handler()
handler = Handler()
