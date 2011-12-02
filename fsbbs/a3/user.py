from twisted.internet import defer

class User(object):
    """ class representing the basic information stored about a user"""
    def _key(self,name):
        return "user:{}:{}".format(self.uid,name)
    @property
    def _hash(self):
        return "user:{}".format(self.uid)
    def _hget(self,name):
        return self.ds.hget(self._hash,name)

    def __init__(self,uid,datasource):
        if uid > 0:
            self.uid = uid
            self.ready = self.load(datasource)


    
    @defer.inlineCallbacks
    def load(self,ds):
        self.ds = ds
        self.username = yield self._hget("username")
        

    @classmethod
    def withProperty(cls,datasource,prop):
        """ 
        returns a redis set (without actually getting it) with
        users having a certain property
        """
        from ..data.types import RSet
        return RSet("userprop:"+prop,datasource)
