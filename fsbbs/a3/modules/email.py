"""
module for mapping email to uid
"""
from zope.interface import implements
from twisted.internet import defer
from ..interface import IAuthModule
from ...data import datasource
from .helpers import addAuthModule


class EmailID(object):
    """ Finds a user by email address"""
    implements(IAuthModule)

    module_type = "authentication"

    def __init__(self):
        self.datasource = datasource.getDatasource()
    
    def precondition(self,chain):
        return chain.uid is None and "email" in chain 
    @defer.inlineCallbacks
    def call(self,chain):
        uid = yield self.datasource.hget("user:email",chain["email"].lower())
        if uid is not None:
            chain.uid = uid
        

addAuthModule(EmailID)


    
