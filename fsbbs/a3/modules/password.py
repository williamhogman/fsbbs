"""
contains modules implementing password authentication
"""
from zope.interface import implements
from ..interface import IAuthModule
from ...data import datasource
from .helpers import addAuthModule
from twisted.internet import defer
from twisted.python import log
import hashlib

class DummyPasswords():
    implements(IAuthModule)

    module_type = "authentication"
    """ 
    Dummy passwords backdoor/plugin. Don't actually use this for anything but debugging
    fsbbs has something for everyone, even crackers ;)
    """
    def __init__(self):
        log.msg("""Dummy passwords running \n"I have a bad feeling about this" """)

    def call(self,chain):
        if "password" in chain and chain['password'] == "id10t":
            chain._success = True
        
addAuthModule(DummyPasswords)

class BasicPasswordMixin:

    def getSalt(self):
        if self._salt is not None:
            return defer.succeed(self._salt)
        def cacheSalt(v):
            self._salt = v
            return v
        d =  self.datasource.get("authmod:BasicPasswords:salt").addCallback(cacheSalt)
        return d
    
    def passwordKey(self,uid):
        return "user:{}:basic_pass".format(uid)


class BasicPasswords(BasicPasswordMixin):
    implements(IAuthModule)

    module_type = "authentication"
    
    def __init__(self,ds=None):
        self.datasource = ds if ds is not None else datasource.getDatasource()
        self._salt = None


    @defer.inlineCallbacks
    def call(self,chain):
        if not "password" in chain:
            return
        elif chain.uid is None:
            return



        pw = yield self.datasource.get("user:{}:basic_pass".format(chain.uid))
        
        if pw is None:
            return

        salt = yield self.getSalt()
        h = hashlib.sha256(salt)
        h.update(chain['password'])
        
        
        if h.digest() == pw:
            chain['valid_basicpassword'] = True
            chain._success = True
        

addAuthModule(BasicPasswords)

        
class ChangeBasicPassword(BasicPasswordMixin):
    implements(IAuthModule)
    module_type="password"
    
    def __init__(self,ds=None):
        self.datasource = ds if ds is not None else datasource.getDatasource()
        self._salt = None
    @defer.inlineCallbacks
    def call(self,chain):
        if chain.failed or not chain._success or not 'new_password' in chain:
            return
        
        salt = yield self.getSalt()

        h = hashlib.sha256(salt)
        h.update(chain['new_password'])
        
        yield self.datasource.set(self.passwordKey(chain.uid),h.digest())
        

addAuthModule(ChangeBasicPassword)        
            

        


            



