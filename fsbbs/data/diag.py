"""
provides a diagnostics daemon for the data module
"""

from .model import Thing,ThingNotFoundError
import datasource
from twisted.internet import defer
from twisted.internet.protocol import Factory
from twisted.protocols.basic import LineReceiver
from zope.interface import implements
from twisted.python import log
from ..diag import DiagProtocol,IDiagFactory

        

class DiagFactory(Factory):
    """ stores the shared state for diag daemon and creates DiagProtocol instance for each connection """
    implements(IDiagFactory)
    servicename = "fsbbs.data"
    protocol = DiagProtocol

    @defer.inlineCallbacks
    def request(self,req):


        if req['reqtype'].lower() == "get":
            try:
                t = Thing(req['id'],self.ds)
                yield t.ready
            except ThingNotFoundError:
                defer.returnValue("Thing not found")
            else:
                defer.returnValue(t)
            



    def __init__(self,service):
        log.msg("launching diag")
        self.ds = datasource.getDatasource()
    
