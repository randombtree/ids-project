# Re-export for easier imports
try:
    from .cache import open_url
    from config import config
    from .debug import debug
except ModuleNotFoundError:
    from .cache import open_url
    from ..config import config
    from .debug import debug



