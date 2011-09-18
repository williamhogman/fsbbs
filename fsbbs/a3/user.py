from twisted.internet import defer

class User:
    def __init__(self,uid,datasource):
        if uid != 0:
            self.uid = uid
            self.load(datasource)


    
    @defer.inlineCallbacks
    def load(self,ds):
        self.ds = ds
        self.username = yield ds.get_by_uid(self.uid,"username")


