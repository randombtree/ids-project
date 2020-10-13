try:
    from config import config
except ModuleNotFoundError:
    from ..config import config

def debug(*args):
    if config.DEBUG:
        print('DEBUG:',*args)
