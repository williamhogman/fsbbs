"""
contains modules implementing password authentication
"""
from zope.interface import implements
from ..interface import IAuthModule
from ...data import datasource
from .helpers import addAuthModule
from twisted.internet import defer
import hashlib

class DummyPasswords():
    implements(IAuthModule)

    module_type = "authentication"
    """ 
    Dummy passwords backdoor/plugin. Don't actually use this for anything but debugging
    fsbbs has something for everyone, even crackers ;)
    """
    def __init__(self):
        print("""Dummy passwords running \n "I have a bad feeling about this" """)

    def call(self,chain):
        if "password" in chain and chain['password'] == "id10t":
            chain._success = True
        
addAuthModule(DummyPasswords)

class BasicPasswords():
    implements(IAuthModule)

    module_type = "authentication"
    
    def __init__(self,ds=None):
        self.datasource = ds if ds is not None else datasource.getDatasource()
        self.datasource.get("authmod:BasicPasswords:salt").addCallback(lambda val: self.salt = val)


    @defer.inlineCallbacks
    def call(self,chain):
        if not "password" in chain or chain.uid is None:
            return

        pw = yield self.datasource.get("user:{}:basic_pass".format(chain.uid))
        
        if pw is None:
            return

        h = hashlib.sha256(self.salt)
        h.update(chain['password'])
        
        
        if h.digest() == pw:
            chain._success = True
        
        
        

try:
    import crack
except ImportError:
    print("we don't have python-crack (cracklib for python) won't load PasswordCrack")
    print("pip install cracklib to install cracklib")
    has_cracklib = False
else:
    has_cracklib = True

if has_cracklib:
    class PasswordCrack():
        implements(IAuthModule)
        
        def call(self,chain):
            
            



