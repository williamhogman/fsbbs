"""
submodule for redis types
"""
import collections
from itertools import imap, ifilter

class RedisType(object):
    def __init__(self,key,ds):
        self.datasource = ds
        if isinstance(key,collections.Callable):
            self._key = key
        else:
            self._key = lambda: key

    @property
    def key(self):
        return self._key()

    def as_key_freeze(self):
        """
        Returns a version with the key to frozen to its current value.
        """
        return self.__class__(self._key(),self.datasource) 
        
class RedisCollectionType(RedisType):
    """ base-class for all redis collection types """

    def map(self, fn):
        """ 
        returns a deferred an imap for the passed in function on the
        items.
        """
        return self.get().addCallback(lambda col: imap(fn, col))

    def filter(self, fn):
        """
        returns a deferred returning an ifilter for the passed in
        function on the items.
        """
        return self.get().addCallback(lambda col: ifilter(fn, col))


    

class RSet(RedisCollectionType):

    def add(self,*items):
        return self.datasource.sadd(self.key,*items)

    def remove(self,*items):
        return self.datasource.srem(self.key,*items)

    def get(self):
        return self.datasource.smembers(self.key)
    
    def is_memeber(self,item):
        return self.datasource.sismember(self.key,item)

    def intersect(self,other):
        if isinstance(other,str):
            okey = other
        else:
            okey = other.key
            
        return self.datasource.sinter(self.key,okey)

