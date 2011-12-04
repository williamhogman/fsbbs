from twisted.internet import defer

from ..a3 import AuthService
from ..a3 import User
from ..data import datasource

from parse import ParsedMessage
from ..service import service
from outgoing import MimeWrap
from ..data.model import ThingNotFoundError
from fsbbs.output.mail import Output

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

        
class RoutedMessage(ParsedMessage):
    """ E-mail messagw with routing information """
    
    def __init__(self,to):
        self.to = to
        ParsedMessage.__init__(self)

    @defer.inlineCallbacks
    def reply(self,headers,template,data=dict()):
        msg = yield Output.render_message(template,data)
        MimeWrap(msg,msg['From'],headers['From']).reply_of(headers).send()
        defer.returnValue(None)

    def send_auth_failed(self,headers):
        return self.reply(headers,"user_not_found")

        
    

class Reply(RoutedMessage):
    """ E-mail message containing a reply to a topic"""

    @defer.inlineCallbacks
    def message_parsed(self,(headers,body)):
        user = yield get_user_by_addr(headers['From'])

        if user is None: 
            self.send_auth_failed(headers)
            defer.returnValue(None)

        try:
            tid = int(self.to[self.to.find("-") + 1:])
        except:
            self.reply(headers,"delivery_failed",dict(to_addr=self.to))
            defer.returnValue(None)
            
        try:
            yield service.postToThing(tid,"\n".join(body),user)
        except ThingNotFoundError:
            self.reply(headers,"thing_not_found",dict(tid=tid))
        else:
            self.reply(headers,"reply_successful")


class Post(RoutedMessage):
    """Email message containing a new topic"""

    @defer.inlineCallbacks
    def message_parsed(self,(headers,body)):
        user = yield get_user_by_addr(headers['From'])
        if user is None:
            self.send_auth_failed()
            defer.returnValue(None)
        
        try:
            tid = int(self.to[self.to.find("-") + 1:])
        except:
            self.reply(headers,"delivery_failed",dict(to_addr=self.to))
            defer.returnValue(None)

        try:
            yield service.newTopic(tid,headers['Subject'],"\n".join(body),user)
        except ThingNotFoundError:
            self.reply(headers,"thing_not_found",dict(tid=tid))
        else:
            self.reply(headers,"post_successful")

        defer.succeed(None)


    
