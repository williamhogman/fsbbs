from .diag import DiagFactory
import datasource
from twisted.internet import reactor
from twisted.python import log
log.msg("""running diag for the fsbbs.data
be careful with this it allows db access to EVERYONE
""")


reactor.listenTCP(8734,DiagFactory(datasource.getDatasource()))
reactor.run()



