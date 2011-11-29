from twisted.internet import defer

from ..a3 import AuthService
from ..a3 import User
from ..data import datasource

from parse import ParsedMessage
from ..service import service
from outgoing import ErrorMessage



@defer.inlineCallbacks
def get_uid_by_addr(sender):
    """ gets a username by email"""
    authserv = AuthService()
    chain = authserv.getChain("email")
    res = yield chain.run({"email": sender})
    
    if res is None or not res.success: defer.returnValue(None)
    defer.returnValue(res.uid)
    
def get_user_by_addr(sender):
    def inner(uid):
        if uid is not None:
            return User(uid,datasource.getDatasource())
        
    return get_uid_by_addr(sender).addCallback(inner)

        

class Reply(ParsedMessage):
    """ E-mail message containing a reply to a topic"""

    def __init__(self,to):
        self.to = to
        ParsedMessage.__init__(self)

    @defer.inlineCallbacks
    def message_parsed(self,(headers,body)):
        user = yield get_user_by_addr(headers['From'])

        if user is None: 
            ErrorMessage("User not found").send(headers['From'])
            defer.returnValue(None)
        
        dash = self.to.find("-") + 1
        if not dash:
            ErrorMessage("An id is required to post").send(headers['From'])
            defer.returnValue(None)
            
        tid = int(self.to[dash:])
        yield service.postToThing(tid,"\n".join(body),user)


class Post(ParsedMessage):
    """Email message containing a new topic"""

    def message_parsed(self,(header,body)):
        return defer.succeed(None)


    
