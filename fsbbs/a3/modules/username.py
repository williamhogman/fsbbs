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


class RegisterUser:
    implements(IAuthModule)
    
    module_type = "register"

    def __init__(self,ds=None):
        self.datasource = ds if ds is not None else datasource.getDatasource()

    @defer.inlineCallbacks
    def call(self,chain):
        # username taken
        if chain.uid is not None: # if there is a UID here we have to stop the process
            chain.failure = True
            return
        elif not 'username' in chain or chain.failure:
            return
        
        
         uid = yield self.datasource.incr("user:next_uid")


        username = chain['username']
        # set up pointers between uname and pw
        self.datasource.set("username:{}:uid".format(username),uid)

        self.datasource.set("user:{}:username".format(uid),username)


        chain._success = True
        
addAuthModule(RegisterUser)
        
