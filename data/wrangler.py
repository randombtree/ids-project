import pandas as pd
import os

try:
    from lib import debug
    import data.weather as weather, data.energy as energy, data.properties as properties
    import data.seasonal_anomalities as seasonal_anomalities
except ModuleNotFoundError:
    from ..lib import debug
    from ..data import weather, energy, properties, seasonal_anomalities

# Directory for store
DATA_STORE = 'datastore'

class get_data:
    """
    Simple wrapper to retrieve stored data or else fetch it via a hook
    usage:
    - df = get_data('key').or_fail()              # Fails if there is no data in store
    - df = get_data('key').or_else(generate_data) # Generates data if there is no data
    """
    def __init__(self, name):
        self.fn = f'{DATA_STORE}/{name}.csv'

    def or_fail(self):
        return pd.read_csv(self.fn, index_col = 0)

    def or_else(self, cb):
        try:
            return self.or_fail()
        except IOError:
            # File not found, ignore
            pass
        # Infer to callback
        df = cb()
        df.to_csv(self.fn)
        return df
# / get_data

def fetch_data():
    """
    Fetch data from original sources and wrangle to appropriate dataframes.
    """
    if not os.path.exists(DATA_STORE):
        debug(f'Creating data store directory at {DATA_STORE}/')
        os.mkdir(DATA_STORE)

    properties_df = get_data('properties').or_else(
        lambda: properties.get_properties())
    temp_df = get_data('decade_temperatures').or_else(
        lambda: weather.get_decade_temperatures())
    avgtemp_df = get_data('avg_temperatures').or_else(
        lambda: weather.get_monthly_averages(temp_df))
    heating_models = get_data('heating_models').or_else(
        lambda: energy.generate_heating_models(properties_df, temp_df))
    heated_buildings = get_data('heated_buildings').or_else(
        lambda: pd.concat([properties_df, heating_models], axis = 1).drop(
            heating_models[heating_models.datapoints.isna()].index)
    )
    anomalities = get_data('seasonal_anomalities').or_else(
        lambda: seasonal_anomalities.get_seasonal_anomalities())
    return {
        'buildings': heated_buildings,
        'temperatures': temp_df,
        'avg_temperatures': avgtemp_df,
        'seasonal_anomalities': anomalities,
    }
