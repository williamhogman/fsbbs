import txredisapi
from twisted.internet import defer
from .. import config

class DataSourceFactory:
    """Factory class for creating datasources"""
    def __init__(self):
        self.load()

    def load(self):
        host = config.get("redis.host")
        port = config.get("redis.port")
        pool_size = config.get("redis.pool_size")
        self.api = txredisapi.lazyRedisConnectionPool(host,port, pool_size=pool_size)

    def getConnection(self):
        return DataSource((self.api))

class DataSource:
    """
    Thin wrapper around the redis api If you wanna do mockups or
    provide a different database backend just make your own datasource
    """
    def __init__(self,api):
        self.api = api

    def get(self,key):
        return self.api.get(key)

    def set(self,key,value):
        return self.api.set(key,value)
    
    def incr(self,key,am=1):
        return self.api.incr(key,am)

    def zrange(self,key,start=0,stop=-1):
        return self.api.zrange(key,start,stop)
    
    def zadd(self,key,score,value):
        return self.api.zadd(key,score,value)
    
    def mget(self,*args):
        return self.api.mget(*args)

    def hget(self,*args,**kwargs):
        return self.api.hget(*args,**kwargs)

# dsf is our singleton datasource factory
dsf = DataSourceFactory()

def getDatasource():
    """ returns a datasource for anywhere"""
    return dsf.getConnection()
    

