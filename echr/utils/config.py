import yaml

__config = None

def config(path='config.yml'):
    global __config
    if __config is None:
        try:
            with open(path) as f:
                __config = yaml.safe_load(f)
                return __config
        except Exception as e:
            print('Could not log configuration file:')
            print(e)
            exit(1)
    return __config