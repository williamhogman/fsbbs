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
        """Called when bot has succesfully signed on to server."""
        map(self.join,self.factory.channels)

    def joined(self, channel):
        """This will get called when the bot joins the channel."""


    def privmsg(self, user, channel, msg):
        """This will get called when the bot receives a message."""
        user = user.split('!', 1)[0]
        
        # Check to see if they're sending me a private message
        if channel == self.nickname:
            msg = "I'm the fsbbs IRC-bot!"
            self.msg(user, msg)
            return

        # Otherwise check to see if it is a message directed at me
        if msg.startswith(self.nickname + ":"):
            self.msg(channel, "I'm the fsbbs IRC-bot")

    def action(self, user, channel, msg):
        """This will get called when the bot sees someone do an action."""
        user = user.split('!', 1)[0]

    def announce(self,message):
        for chan in self.factory.channels:
            self.say(chan,message,256)
        

    # For fun, override the method that determines how a nickname is changed on
    # collisions. The default method appends an underscore.
    def alterCollidedNick(self, nickname):
        """
        Generate an altered version of a nickname that caused a collision in an
        effort to create an unused related name for subsequent registration.
        """
        return nickname + '^'



class NotifyIRCBotFactory(protocol.ClientFactory):
    """
    Factory for IrcNotifyBot
    A new protocol instance will be created each time we connect to the server.
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

    def process(self,notf):
        for server in self.servers:
            server.announce(notf.kind)
        return defer.returnValue(None)

