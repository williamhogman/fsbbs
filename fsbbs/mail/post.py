from twisted.internet import defer

from parse import ParsedMessage

class Reply(ParsedMessage):
    """ E-mail message containing a reply to a topic"""

    def message_parsed(self,(headers,body)):
        return defer.succeed(None)


class Post(ParsedMessage):
    """Email message containing a new topic"""

    def message_parsed(self,(header,body)):
        return defer.succeed(None)


    
