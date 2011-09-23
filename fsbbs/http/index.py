import cyclone.web
from twisted.internet import defer
from ..service import service

class IndexHandler(cyclone.web.RequestHandler):
    @defer.inlineCallbacks
    def get(self):
        fp = yield service.getFrontpage()        
        if "msg" in fp:
            self.write(fp['msg']['msg'])

        self.write(str(fp["main"]))


 
