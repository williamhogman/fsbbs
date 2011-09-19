"""
modules for doing the username to uid
"""
from zope.interface import implements
from ..interface import IAuthModule
from ...data import datasource
from .helpers import addAuthModule
from twisted.internet import defer



class BasicUsername:
    implements(IAuthModule)


    module_type = "authentication"

    def __init__(self):
        self.datasource = datasource.getDatasource()

    @defer.inlineCallbacks
    def call(self,chain):
        #uid found already
        if chain.uid is not None:
            return

        username = chain['username'].lower()


        uid = yield self.datasource.get("username:{}:uid".format(chain['username']))
        if uid is not None:
            chain.uid = uid
        
        
    
addAuthModule(BasicUsername)
