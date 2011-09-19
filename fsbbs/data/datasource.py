import txredisapi

class DataSourceFactory:
    def __init__(self):
        self.api = txredisapi.lazyRedisConnectionPool("127.0.0.1",6379, pool_size=2)

    def getConnection(self):
        return DataSource(self.api)

class DataSource:
    def __init__(self,api):
        self.api = api

    def get(self,key):
        return self.api.get(key)

    def set(self,key,value):
        return self.api.set(key,value)


dsf = DataSourceFactory()
def getDatasource():
    return dsf.getConnection()
    
