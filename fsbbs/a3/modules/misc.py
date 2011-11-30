from zope.interface import implements
from ..interface import IAuthModule
from .helpers import addAuthModule

class ValidUID(object):
    implements(IAuthModule)
    """ 
    Authentication scheme where finding a valid user id is considered authentication.
    Use with care! This module is togheter with the EmailID in the stock fsbbs distro.
    """
    def precondition(self,chain):
        return chain.uid is not None
    def call(self,chain):
        chain._success = True

addAuthModule(ValidUID)
