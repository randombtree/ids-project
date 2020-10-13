# Weird imports: this is so that this repo can also be used as an external library
# - Python has this weird thing going on with relative import paths..

try:
    from data.seasonal_anomalities import get_seasonal_anomalities
    from data.properties import get_properties
except ModuleNotFoundError:
    from .seasonal_anomalities import get_seasonal_anomalities
    from .properties import get_properties
