from zope.interface import Interface

class IOutgoingMailProvider(Interface):
    def send(message):
        """ sends the passed in message as an email """
    
