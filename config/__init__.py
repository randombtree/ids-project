class Configuration:
    """
    Dictionary wrapper for config.
    Allows us to access configuration items with fewer keystrokes, e.g.
    config.DEBUG instead of using a dictionary with config['DEBUG']
    """
    def __init__(self, d):
        self._d = d
    # Array-accessors (for assignment mostly)
    def __delitem__(self, key):
        raise KeyError('Configuration values can\'t be removed')
    def __getitem__(self, key):
        return self._d[key]
    def __setitem__(self, key, value):
        self._d[key] = value

    def __getattr__(self, n):
        if n in self._d:
            return self._d[n]
        raise AttributeError(f'No configuration available for {n}')

config = Configuration({
    'DEBUG': True,
})

# TODO: Read/Write config file if deemed necessary
