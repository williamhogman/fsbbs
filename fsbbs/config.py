
def _load():
    import yaml
    with open("config.yaml") as f:
        return yaml.load(f)

_data = _load()

def get(key):
    parts = key.split(".")
    
    cur = _data[parts[0]]
    for part in parts[1:]:
        cur = cur[part]

    return cur

        





