import txredisapi
from twisted.internet import defer

class DataSourceFactory:
    def __init__(self):
        self.load()

    def load(self):
        self.api = txredisapi.lazyRedisConnectionPool("127.0.0.1",6379, pool_size=2)

    def getConnection(self):
        return DataSource((self.api))

class DataSource:
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

dsf = DataSourceFactory()
def getDatasource():
    return dsf.getConnection()
    

