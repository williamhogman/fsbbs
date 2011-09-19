authModules = dict()

def addAuthModule(mod):
    name = mod.__name__
    if  name in authModules:
        print("duplicate module found")
    else:
        authModules[name] = mod
        print("added {}".format(name))
