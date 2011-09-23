from .diag import DiagFactory
import datasource
from twisted.internet import reactor

print("running diag for the fsbbs.data")
print("be careful with this it allows db access to EVERYONE")
print("seriously...")

reactor.listenTCP(8734,DiagFactory(datasource.getDatasource()))
reactor.run()



