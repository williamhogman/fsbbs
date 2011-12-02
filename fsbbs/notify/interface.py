from zope.interface import Interface


class INotificationService(Interface):
    """ Interface for services that send notifications to our users """
    def process(notf):
        """processes an incoming notification and sends it along as neccessary"""



