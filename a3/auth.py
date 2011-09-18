
from user import User
from zope.interface import Interface,Attribute,implements

class IAuthModule(Interface):
    module_type = Attribute("""returns the type of the module. one of the PAM module types""")

    def call(chain):
        """ call this auth module """


class AuthHardFailure(Exception):
    """ if raised by an authmodule causes the 
        entire authentication process to fail with 
        no chance of recovering """


class AuthChain:
    """ calls the authentication modules that are used"""
    def __init__(self):
        self.done = False
        self._hardfailure = False
        self.uid = None
        self.data = dict()


    def failHard(self):
        self._hardfailure = True
    def hasHardFailed(self):
        return self._hardfailure


    @property
    def success(self):
        """ Gets if we have been successful. we must also have decided on uid. 
            the auth process has to be done and successful. no unfixed failures
        """
        if self.done and self._success and and self.uid is not None and !self.failed:
            return True


    @success.setter
    def success(self,value):
        """ sets success to the passed in value unless we hardfailed """
        if not self._hardfailure:
            self._success = value
                
        

    @property 
    def failed(self):
        """ 
        gets the failure state. If we failed hard we've failed. If we failed we've failed
        if we are done and successful we haven't failed, otherwise we failed.
        """
        return self._failure or self._hardfailure
        if self._hardfailure:
            return True
        if self._failure:
            return True

        return False
        
    
    @failed.setter
    def failed(self,value):
        """ sets failure to value unless we hard failed in which case setting failure has no effect"""
        if not self._hardfailure:
            self._failure= value
        
    


class BannedModule:
    """
    This module provides banning for an ip address 
    or a uesrname. It checks the  keys
    banned_ip:$ip  and banned_user:$username

    Note: this module is intended for blocking intrusion attempts not
          ordinary abusive users, they are to be handled by putting
          them in a group that doesn't have permission to post
          IP address blocking should be avoided.


    this does not check that the actual username exists.
    The lack of username verification is intentional as 
    this allows you to globally block login atempts for root or admin

    Sets the following values on the chain
    
    hardFail: hardFail is called if a delay value under zero is found. 
              This effectively blocks the authentication


    delay: if it finds a value that is over zero it sets a delay that is 
           by which the authentication process should be delayed

    """
    implements(IAuthModule)
    module_type = "authentication"

    def call(self,chain):
        # we don't touch the data when the user might be logged in
        if "session_secret" in chain:
            return data

        if "ipaddr" in chain:
            #check against block list
            pass
        if "username" in chain:
            #check against block list
            pass
        
        ## passed our tests
            
