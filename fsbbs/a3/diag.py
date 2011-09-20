"""
fsbbs.a3 diagnostics daemon
"""

from twisted.internet import defer
from twisted.internet.protocol import Factory
from twisted.protocols.basic import LineReceiver


class DiagProtocol(LineReceiver):
    """ Implements the diagnostics line protocol"""
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
    """ stores the shared state for diag daemon and creates DiagProtocol instance for each connection """
    protocol = DiagProtocol

    def request(self,req):

        def formatOutput(chain):
            chain.data['failure'] = chain.failed
            chain.data['success'] = chain.success
            chain.data['uid'] = chain.uid
            return chain.data


        d = defer.Deferred()        
        if req['reqtype'].lower() == "echo":
            d.callback(req)
        elif req['reqtype'].lower() == "auth":
            self.service.getChain("diag").run(req,formatOutput).addCallback(d.callback)
        elif req['reqtype'].lower() == "change":
            self.service.getChain("changepassword").run(req,formatOutput).addCallback(d.callback)
        elif req['reqtype'].lower() == "register":
            self.service.getChain("register").run(req,formatOutput).addCallback(d.callback)

        return d

            
        




    def __init__(self,service):
        print("launching diag")
        self.service = service
