from zope.interface import implements
from ..interface import IAuthModule
from ...data import datasource
from .helpers import addAuthModule
from twisted.internet import defer
from twisted.python import randbytes



class SessionSecretModule:
    implements(IAuthModule)

    def __init__(self,ds=None):
        self.datasource = ds or datasource.getDatasource()


    module_type = "authentication"

    @defer.inlineCallbacks
    def call(self,chain):
        if not "session_secret" in chain:
            return
        uid = yield self.datasource.get("session:"+chain['session_secret'])
        if uid is not None:
            chain.uid = uid


            # session has been limited by ip
            if 'remote-addr' in data:
                sess_ip = yield self.datasource.get("session-ip:"+chain['session_secret'])                
                if sess_ip != data['remote-addr']: 
                    chain['attack-session-hijack'] = True                   
                    chain.failHard() # Session hijacking probably
                    return
            
            chain._success = True


addAuthModule(SessionSecretModule)

class SessionStorageModule:
    implements(IAuthModule)

    module_type = "session"

    def __init__(self,ds=None):
        self.datasource = ds or  datasource.getDatasource()

    @defer.inlineCallbacks
    def call(self,chain):
        # if we already have a session don't recreate it.
        if  "session_secret" in chain:
            return
        # we need an UID before signing in and we need to have been successful atleast once
        if chain.uid is None or not chain._success:
            return

        # twisted.python.randbytes is basically just an alias for os.urandom 
        # it handles fallbacks etc and throws an exception if we don't have a
        # secure random source
        rand = randbytes.secureRandom(16)  
        
        session_secret = rand.encode("hex") # should probably use something more efficent than hex here...
        
        chain['set_session_secret'] = session_secret
        yield self.datasource.set("session:"+session_secret,chain.uid)


        # if an IP address has been specified in the chain
        # set it in the data store

        if "ipaddr" in chain:
            self.datasource.set("session-ip:"+session_secret,chain['ipaddr'])

addAuthModule(SessionStorageModule)
