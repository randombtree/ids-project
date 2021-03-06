# Weird imports: this is so that this repo can also be used as an external library
# - Python has this weird thing going on with relative import paths..

try:
    from data.seasonal_anomalities import get_seasonal_anomalities
    from data.properties import get_properties
    from data.energy import get_monthly_energy_data, get_decade_heat_data, generate_heating_models
    from data.weather import get_decade_temperatures
except ModuleNotFoundError:
    from .seasonal_anomalities import get_seasonal_anomalities
    from .properties import get_properties
    from .energy import get_monthly_energy_data, get_decade_heat_data, generate_heating_models
    from .weather import get_decade_temperatures
