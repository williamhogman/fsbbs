"""
Notification module for twisted.words.im
"""
from zope.interface import implements
from twisted.words.protocols import irc
from twisted.internet import reactor, protocol, defer

from fsbbs.notify.interface import INotificationService
from fsbbs import config


class NotifyIRCBot(irc.IRCClient):
    """IRC bot sending fsbbs notifications"""
    
    def __init__(self, nickname, realname):
        self.nickname = nickname
        self.realname = realname

    
    def connectionMade(self):
        irc.IRCClient.connectionMade(self)
        self.factory.client = self

    def connectionLost(self, reason):
        irc.IRCClient.connectionLost(self, reason)


    def signedOn(self):
        """Called when connected joins our channels."""
        map(self.join,self.factory.channels)

    def joined(self, channel):
        """When the bot joins a channel, does nothing in our case."""


    def privmsg(self, user, channel, msg):
        """This will get called when the bot receives a message. For now just tell them we are fsbbs"""
        user = user.split('!', 1)[0]
        msg = "I'm the fsbbs IRC-bot!"
        if channel == self.nickname:
            self.msg(user, msg)
            return

        if msg.startswith(self.nickname + ":"):
            self.msg(channel, msg)

    def announce(self,message):
        for chan in self.factory.channels:
            self.say(chan,message,256)
        

    def alterCollidedNick(self, nickname):
        """
        Generate an altered version of a nickname that caused a collision in an
        effort to create an unused related name for subsequent registration.
        """
        return nickname + '^'



class NotifyIRCBotFactory(protocol.ClientFactory):
    """
    Factory keeping track of our connection to an irc server
    """

    def __init__(self, nick, realname, channels):
        self.nick = nick
        self.realname = realname
        self.channels = channels

    def buildProtocol(self, addr):
        p = NotifyIRCBot(self.nick,self.realname)
        p.factory = self
        return p

    def clientConnectionLost(self, connector, reason):
        """If we get disconnected, reconnect to server."""
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print("Connection failure for irc notify")

    def announce(self,message):
        self.client.announce(message)
        


class IMNotificationService(object):
    implements(INotificationService)
    
    handles = ["new_topic","new_reply"]

    def __init__(self):
        server_conf = config.get("notify.im.servers")
        self.servers = list()

        for server in server_conf:
            if server["type"] == "irc":
                bot = NotifyIRCBotFactory(server["nickname"],
                                          server["realname"],
                                          server["channels"])
                reactor.connectTCP(server["hostname"],server["port"],bot)
            self.servers.append(bot)

    def _handle_new_topic(self,notf):
        title = notf.obj["topic"].title
        return "New topic - {}".format(title)
    def _handle_new_reply(self,notf):
        title = notf.obj["parent"].title
        return "A reply has been made to '{}'".format(title)
    
    def process(self,notf):
        if notf.kind in self.handles:
            message = getattr(self,"_handle_"+notf.kind)(notf)
        else:
            return defer.succeed(None)

        for server in self.servers:
            server.announce(message)
        return defer.succeed(None)

