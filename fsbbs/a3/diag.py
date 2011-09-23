"""
fsbbs.a3 diagnostics daemon
"""

from twisted.internet import defer
from twisted.internet.protocol import Factory
from twisted.protocols.basic import LineReceiver
from zope.interface import implements
from ..diag import DiagProtocol,IDiagFactory

        
class DiagFactory(Factory):
    """ stores the shared state for diag daemon and creates DiagProtocol instance for each connection """
    implements(IDiagFactory)
    servicename = "fsbbs.a3"

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
