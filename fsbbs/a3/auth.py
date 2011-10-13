
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
          "register": ["BasicUsername","RegisterUser","ChangeBasicPassword","SessionStorageModule"],
          "session": ["SessionSecretModule"]
          }    
    

class AuthService:
    """ provides a service interface for the authentication system"""
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
    """ A chain of AuthModules to call during the authentication process, keeps shared state thru the process"""
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
        """Runs the authchain using the passed in data and an optional callback"""
        self.data = data


        d = defer.Deferred()
        

        def logFromModule(module,msg):
            """logs a message from a module """
            log.msg("{} {}".format(module.__class__.__name__,msg))

        def moduleLog(module):
            """ logs information about the state of a module after it has run"""
            logFromModule(module,"success:{} failed:{}".format(self._success,self.failed))

        def callModule(arg,module):
            """calls a module this includes processing preconditions"""
            shouldRun = module.precondition(self) if hasattr(module,"precondition") else True

            if shouldRun:
                d = defer.maybeDeferred(module.call,self)
                d.addCallbacks(lambda arg: moduleLog(module))
            else:
                        
                d = defer.succeed(None)
            return d

        for module in self.modules:
            d.addCallback(callModule,module)

        def onDone(chain):
            log.msg("AuthChain has run till completetion")
            self.done = True
            return self



        d.addCallback(onDone)
        # add optional callback
        if cb is not None:
            d.addCallback(cb)

        d.addErrback(log.err)
        d.callback(self)
        return d
        
        
     



    def failHard(self):
        """ cause the module to fail into an unrecoverable state,
        this means that the chain will never be successful"""
        self._hardfailure = True
    def hasHardFailed(self):
        return self._hardfailure

    @property
    def audit(self):
        """ gets a tuple with the actual state of the auth chain. """
        return (self.done,self._success,self.uid,self.failed)

    @property
    def success(self):
        """ Gets if we have been successful. we must also have decided on uid. 
            the auth process has to be done and successful. no unfixed failures
        """
        return self.done and self._success and self.uid is not None and not self.failed

    @success.setter
    def success(self,value):
        if not self._hardfailure:
            self._success = value

                

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
        
    









