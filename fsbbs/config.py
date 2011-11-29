def _load():
    import yaml
    with open("config.yaml") as f:
        return yaml.load(f)


def _run():
    import sys

    cfg = _load()
    module = sys.modules[__name__] 
    def inner(data,into):
        for key,val in data.items():
            if isinstance(val,dict):
                setattr(into,key,inner(val,type('new',(object,))))
            else:
                setattr(into,key,val)
    inner(cfg,module)
    

_run()
                            

        





