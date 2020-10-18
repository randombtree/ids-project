#!/usr/bin/env python3
# IDS Project 2020
# Gather data from original data-sources and store it processed locally

import data
import os
import pandas as pd
from lib import debug

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

def main():
    if not os.path.exists(DATA_STORE):
        debug(f'Creating data store directory at {DATA_STORE}/')
        os.mkdir(DATA_STORE)

    properties_df = get_data('properties').or_else(
        lambda: data.get_properties())
    temp_df = get_data('decade_temperatures').or_else(
        lambda: data.get_decade_temperatures())
    heating_models = get_data('heating_models').or_else(
        lambda: data.generate_heating_models(properties_df, temp_df))
    heated_buildings = get_data('heated_buildings').or_else(
        lambda: pd.concat([properties_df, heating_models], axis = 1).drop(
            heating_models[heating_models.datapoints.isna()].index)
    )

if __name__ == '__main__':
    main()
