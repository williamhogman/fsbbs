from .diag import DiagFactory
from .auth import AuthService
from twisted.internet import reactor

print("starting fsbbs A3 diagnostics server")
print("WARNING fsbbs.diag.a3 provides anonymous access to diagnostic information about the a3 system")
print("IF THIS IS A PRODUCTION ENVIRONMENT ABORT NOW")

reactor.listenTCP(8733,DiagFactory(AuthService()))
reactor.run()

