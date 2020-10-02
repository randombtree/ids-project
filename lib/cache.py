import os
import urllib.request as urlreq
import hashlib
from .debug import debug

CACHE_PATH = 'cache'
BUF_SIZE = 4096

def create_cachedir():
    if not os.path.exists(CACHE_PATH):
        debug(f"Creating cache directory for requests at {CACHE_PATH}/")
        os.mkdir(CACHE_PATH)

def cached_name(name):
    """
    Return the cache path for name
    """
    hashname = hashlib.sha1(name.encode()).hexdigest()
    return f'{CACHE_PATH}/{hashname}'

def has_cached(name):
    return os.path.isfile(cached_name(name))

def open_cached(name, mode='r'):
    """
    Open file from cache. Check if file exists with has_cached first (if not overwriting /
    handling exception)
    """
    create_cachedir()
    return open(cached_name(name), mode=mode)

def open_url(url, mode='r', cached = True, update = False):
    """
    Returns a read handle for URL, either cached or not.
    mode: File mode, defaults to 'r', but 'rb' should be used on pure binary files.
    cached: Try to cache object / retrieve cached object if available (default = yes)
    update: Validate cached object from server (if-modified-since) (default = no, unimplemented for now)
    """
    cached_url = cached_name(url)
    create_cachedir()
    if not cached or not os.path.isfile(cached_url):
        # Not in/from cache
        # The contents are always written to disk first; if url misbehaves this is were we fall
        # not at some random dataframe creation routine.
        with urlreq.urlopen(url) as f:
            # we get a binary stream at this point, write it as such:
            with open(cached_url, mode='wb') as out:
                while True:
                    data = f.read(BUF_SIZE)
                    out.write(data)
                    if len(data) != BUF_SIZE:
                        break
    else:
        debug(f'Returning cached {url}')
    fh = open(cached_url, mode=mode)
    if not cached:
        debug(f'Removing cached instance for {url}')
        # cached = False also implies no disk space wasted for url content
        os.unlink(cached_url)
    return fh
