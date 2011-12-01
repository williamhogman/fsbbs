"""
submodule for redis types
"""
import collections

class RedisType(object):
    def __init__(self,key,ds):
        self.datasource = ds
        if isinstance(key,collections.Callable):
            self.key = property(key)
        else:
            self.key = key

class RSet(object):
    def add(self,*items):
        return self.datasource.sadd(self.key,*items)

    def remove(self,*items):
        return self.datasource.srem(self.key,*items)

    def get(self):
        return self.datasource.smembers(self.key)
    
    def is_memeber(self,item):
        return self.datasource.sismember(self.key,item)

