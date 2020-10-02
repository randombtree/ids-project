from ..config import config

def debug(*args):
    if config.DEBUG:
        print('DEBUG:',*args)
