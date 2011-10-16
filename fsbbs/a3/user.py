from twisted.internet import defer

class User(object):
    """ class representing the basic information stored about a user"""
    def _key(self,name):
        return "user:{}:{}".format(self.uid,name)
    def __init__(self,uid,datasource):
        if uid > 0:
            self.uid = uid
            self.ready = self.load(datasource)


    
    @defer.inlineCallbacks
    def load(self,ds):
        self.ds = ds
        self.username = yield self.ds.get(self._key("username"))
