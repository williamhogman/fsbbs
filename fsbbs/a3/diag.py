"""
fsbbs.a3 diagnostics daemon
"""

from twisted.internet import defer
from twisted.internet.protocol import Factory
from twisted.protocols.basic import LineReceiver


class DiagProtocol(LineReceiver):
    def writeResponse(self,response):
        self.sendLine("Response")
        for k,v in response.iteritems():
            self.sendLine("{}: {}".format(k,v))
        self.bfr = None
        

    def connectionMade(self):
        self.sendLine("Connected to fsbbs.diag.a3")

    def lineReceived(self,line):

        if not hasattr(self,"bfr") or self.bfr is None:
            self.bfr = dict(reqtype=line.strip())
        elif line=="":
            # we dont wanna parse an empty request
            if len(self.bfr) > 0:
                self.factory.request(self.bfr).addCallback(self.writeResponse)
        else:
            i = line.find(":")
            name = line[:i].strip()
            val = line[i+1:].strip()
            self.bfr[name] = val
        
class DiagFactory(Factory):
    protocol = DiagProtocol

    def request(self,req):

        d = defer.Deferred()        
        if req['reqtype'].lower() == "echo":
            d.callback(req)
        elif req['reqtype'].lower() == "auth":
            print("auth")
            def doAuth(chain):
                print("derp")
                d =  chain.data
                chain.data['failure'] = chain.failed
                chain.data['success'] = chain.success
                chain.data['uid'] = chain.uid
                return d
                
            self.service.getChain("diag").run(req,doAuth).addCallback(d.callback)


        return d

            
        




    def __init__(self,service):
        print("launching diag")
        self.service = service
