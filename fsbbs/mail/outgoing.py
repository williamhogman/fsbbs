
class OutgoingMessage(object):
    def send(self):
        print(self)

class ErrorMessage(OutgoingMessage):
    def __init__(self,msg):
        self.msg = msg
