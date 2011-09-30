from twisted.python import  log
authModules = dict()

def addAuthModule(mod):
    name = mod.__name__
    if  name in authModules:
        log.msg("duplicate module found, {} already loaded".format(name))
    else:
        authModules[name] = mod
        log.msg("added {}".format(name))
