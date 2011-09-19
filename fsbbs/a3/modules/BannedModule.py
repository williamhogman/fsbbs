from zope.interface import implements
from ..interface import IAuthModule
from ...data import datasource
from .helpers import addAuthModule

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
    
    def __init__(self,block_ip=[],block_user=["root","admin"]):
        self.block_ip = block_ip
        self.block_user = block_user


    def call(self,chain):

        # we don't touch the data when the user might be logged in
        if "session_secret" in chain:
            pass

        if "ipaddr" in chain:
            if chain['ipaddr'] in self.block_ip:
                chain.failHard()

                
        if "username" in chain:
            #check against block list
            if chain['username'] in self.block_user:
                chain.failHard()


        
        ## passed our tests
            
addAuthModule(BannedModule)
