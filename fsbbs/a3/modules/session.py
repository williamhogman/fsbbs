from ..interface import IAuthModule
from ...data import datasource
from .helpers import addAuthModule
from twisted.internet import defer
from twisted.python import randbytes
import binascii

# sessions expire after a week of inactivity, verification refreshes the ttl
SESSION_TTL = 7 * 24 * 3600


class SessionSecretModule:
    """Verifies session secrets stored in a redis backend"""

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


            # if the session was bound to an ip when it was created, enforce it
            sess_ip = yield self.datasource.get("session-ip:"+chain['session_secret'])
            if sess_ip is not None and 'ipaddr' in chain:
                if sess_ip != chain['ipaddr']:
                    chain['attack-session-hijack'] = True
                    chain.failHard() # Session hijacking probably
                    return

            # sliding expiry: keep the session alive while it is being used
            yield self.datasource.expire("session:"+chain['session_secret'],SESSION_TTL)
            yield self.datasource.expire("session-ip:"+chain['session_secret'],SESSION_TTL)

            chain._success = True


addAuthModule(SessionSecretModule)

class SessionStorageModule:
    """ Stores sesison secrets upon successful login, also providings rudimentary session-hijacking protections"""

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
        
        session_secret = binascii.hexlify(rand).decode("ascii") # should probably use something more efficent than hex here...
        
        chain['set_session_secret'] = session_secret
        yield self.datasource.set("session:"+session_secret,chain.uid)
        yield self.datasource.expire("session:"+session_secret,SESSION_TTL)


        # bind the session to the ip address it was created from
        # so SessionSecretModule can detect hijacking attempts

        if "ipaddr" in chain:
            yield self.datasource.set("session-ip:"+session_secret,chain['ipaddr'])
            yield self.datasource.expire("session-ip:"+session_secret,SESSION_TTL)

addAuthModule(SessionStorageModule)
