from twisted.internet import defer
from twisted.internet.protocol import Factory
from twisted.protocols.basic import LineReceiver
from zope.interface import Interface,Attribute,implements

class DiagProtocol(LineReceiver):
    """ Implements the diagnostics line protocol"""
    def writeResponse(self,response):
        self.sendLine("Response")
        for k,v in response.iteritems():
            self.sendLine("{}: {}".format(k,v))
        self.bfr = None
        

    def connectionMade(self):
        self.sendLine("Connected to {} on {}".format(self.factory.servicename,self.factory.hostname))

    def lineReceived(self,line):

        if not hasattr(self,"bfr") or self.bfr is None:
            self.bfr = dict(reqtype=line.strip())
        elif line=="":
            # we dont wanna parse an empty request
            if len(self.bfr) > 0:
                self.factory.request(self.bfr).addCallback(self.writeResponse)
        else:
            i = line.find(":")
            name = line[:i].strip()
            val = line[i+1:].strip()
            self.bfr[name] = val



class IDiagFactory(Interface):
    def request(arg):
        """ called on to process a request"""

    
