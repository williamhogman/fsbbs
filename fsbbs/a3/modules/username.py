"""
modules for doing the username to uid
"""
from zope.interface import implements
from ..interface import IAuthModule
from ...data import datasource
from .helpers import addAuthModule
from twisted.internet import defer



class BasicUsername:
    """module for finding a username in the redis backend"""
    implements(IAuthModule)


    module_type = "authentication"

    def __init__(self):
        self.datasource = datasource.getDatasource()

    def precondition(self,chain):
        # the UID has not been found yet
        if chain.uid is None:
            return True

        return False


    @defer.inlineCallbacks
    def call(self,chain):
        if not 'username' in chain:
            return

        username = chain['username'].lower()

        uid = yield self.datasource.get("username:{}:uid".format(username))
        if uid is not None:
            chain.uid = uid
        
        
    
addAuthModule(BasicUsername)


class RegisterUser:
    """register a user to the redis backend"""
    implements(IAuthModule)
    
    module_type = "register"

    def __init__(self,ds=None):
        self.datasource = ds if ds is not None else datasource.getDatasource()


    def precondition(self,chain):
        return 'username' in chain and not chain.failed
    @defer.inlineCallbacks
    def call(self,chain):
        # is the username taken
        if chain.uid is not None: # if there is a UID here we have to stop the process
            chain.failure = True
            return
        
        chain.uid = uid = yield self.datasource.incr("user:next_uid")

        username = chain['username']
        # set up pointers between uname and pw
        self.datasource.set("username:{}:uid".format(username),uid)

        self.datasource.set("user:{}:username".format(uid),username)

        chain._success = True
        
addAuthModule(RegisterUser)
        
