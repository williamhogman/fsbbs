
from user import User
from zope.interface import implements
from twisted.internet import defer,reactor
from twisted.python import randbytes,log
from ..data import datasource
from .interface import IAuthModule
#every module is responsible for calling addAuthModule
from .modules import authModules



class AuthHardFailure(Exception):
    """ if raised by an authmodule causes the 
        entire authentication process to fail with 
        no chance of recovering """




chains = {"default": ["BannedModule","SessionSecretModule",
                      "BasicUsername","DummyPasswords","BasicPasswords","SessionStorageModule"],
          "changepassword": ["SessionSecretModule","BasicUsername","BasicPasswords",
                             "DummyPasswords","ChangeBasicPassword"],
          "register": ["BasicUsername","RegisterUser","ChangeBasicPassword"],
          "session": ["SessionSecretModule"]
          }    
    

class AuthService:
    def __init__(self):
        pass
    
    def getChain(self,service):
        ac = AuthChain()
        ac.modules = list()

        chainproto = chains[service] if service in chains else chains['default']
        for mod  in chainproto:
            ac.modules.append(authModules[mod]())

        return ac
        

class AuthChain:
    """ calls the authentication modules that are used"""
    def __init__(self):
        self.done = False
        self._hardfailure = False
        self.uid = None
        self.modules = None
        self._failure = False
        self._success = False


    def __contains__(self,key):
        return self.data.__contains__(key)
    
    def __getitem__(self,key):
        return self.data.__getitem__(key)
    
    def __setitem__(self,key,value):
        return self.data.__setitem__(key,value)

    def __delitem__(self,key):
        return self.data.__delitem__(key)


    def run(self,data,cb=None):
        self.data = data
        # create our defered
        d = defer.Deferred()
        
        def moduleLog():
            print("leaving {} success:{} failed:{} ".format(module,self._success,self.failed))

        def callModule(arg,module):

            d = defer.maybeDeferred(module.call,self)
            d.addCallbacks(lambda arg: moduleLog())
            return d

        for module in self.modules:
            d.addCallback(callModule,module)
        def onDone(chain):
            print("DONE!--")
            self.done = True
            return self



        d.addCallback(onDone)
        if cb is not None:
            d.addCallback(cb)

        d.addErrback(log.err)
        d.callback(self)
        return d
        
        
     



    def failHard(self):
        self._hardfailure = True
    def hasHardFailed(self):
        return self._hardfailure

    @property
    def audit(self):
        return (self.done,self._success,self.uid,self.failed)

    @property
    def success(self):
        """ Gets if we have been successful. we must also have decided on uid. 
            the auth process has to be done and successful. no unfixed failures
        """
        return self.done and self._success and self.uid is not None and not self.failed



                

    @property
    def preliminarySuccess(self):
        """ has the chain had success set to true yet"""
        return self._success and not self._hardfailure

    @property 
    def failed(self):
        """ 
        gets the failure state. If we failed hard we've failed. If we failed we've failed
        if we are done and successful we haven't failed, otherwise we failed.
        """
        return self._failure or self._hardfailure
        
    
    @failed.setter
    def failed(self,value):
        """ sets failure to value unless we hard failed in which case setting failure has no effect"""
        if not self._hardfailure:
            self._failure= value
        
    









