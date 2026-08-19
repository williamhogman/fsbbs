import os
import txredisapi
from twisted.internet import defer

class DataSourceFactory:
    """Factory class for creating datasources"""
    def __init__(self):
        self.load()

    def load(self):
        port = int(os.environ.get("REDIS_PORT", "6379"))
        host = os.environ.get("REDIS_HOST", "127.0.0.1")
        self.api = txredisapi.lazyConnectionPool(host, port, poolsize=2)

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

    def zrevrange(self,key,start=0,stop=-1):
        return self.api.zrevrange(key,start,stop)

    def zadd(self,key,score,value):
        return self.api.zadd(key,score,value)

    def zincrby(self,key,increment,value):
        return self.api.zincrby(key,increment,value)

    def setnx(self,key,value):
        return self.api.setnx(key,value)

    def publish(self,channel,message):
        return self.api.publish(channel,message)

    def mget(self,*args):
        return self.api.mget(*args)

    def delete(self,*keys):
        return self.api.delete(*keys)

    def expire(self,key,ttl):
        return self.api.expire(key,ttl)


# dsf is our singleton datasource factory
# TODO: provid confiurablity
dsf = DataSourceFactory()

def getDatasource():
    """ returns a datasource for anywhere"""
    return dsf.getConnection()
    

