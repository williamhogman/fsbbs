from functools import partial
from twisted.internet import defer
from fsbbs.data.types import RSet,RHash

class User(object):
    """ class representing the basic information stored about a user"""
    __hash_keys = ['username','email']
    def _key(self,name):
        return "user:{}:{}".format(self.uid,name)
    @property
    def _hash(self):
        return "user:{}".format(self.uid)

    def __init__(self,uid,datasource):
        self.ds = datasource
        if uid > 0:
            self.uid = uid
            self.hash = RHash(self._hash,self.ds)
            self.ready = self.load()
    

    @defer.inlineCallbacks
    def load(self):
        main = self.hash.mget(*self.__hash_keys)
        main.addCallback(partial(zip,self.__hash_keys))
        main.addCallback(partial(map,lambda (k,v): setattr(self,k,v)))
        yield main
        



    @classmethod
    @defer.inlineCallbacks
    def by_ids(cls,uids,ds,ready=False):
        users = list()
        for uid in uids:
            users.append(cls(uid,ds))
        if ready:
            yield defer.DeferredList([user.ready for user in users])
        defer.returnValue(users)

    @classmethod
    def with_property(cls,datasource,prop):
        """ 
        returns a redis set (without actually getting it) with
        users having a certain property
        """
        return RSet("userprop:"+prop,datasource)
