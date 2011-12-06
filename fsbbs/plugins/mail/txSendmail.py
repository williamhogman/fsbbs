"""
Plugin for using twisted sendmail as the outgoing mail provider
"""
from zope.interface import implements
from twisted.plugin import IPlugin
from twisted.mail.smtp import sendmail
from twisted.internet import defer
from fsbbs.mail.outgoing import IOutgoingMailProvider
from fsbbs import config

class txSendmail(object):
    """ Handler for Sendmail """
    implements(IPlugin,IOutgoingMailProvider)
    def __init__(self):
        self.smtpserv = config.get("email.outgoing.host")

    @defer.inlineCallbacks
    def send(self, message):
        """ Sends the message using twisted """
        yield sendmail(self.smtpserv,
                       message.sender,
                       message.to,message.as_mime())


txSendmailProvider = txSendmail()
