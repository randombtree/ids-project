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
    """
    def __init__(self, name):
        self.name = name

    def or_fail(self, fn):
        return pd.read_csv(fn, index_col = 0)

    def or_else(self, cb):
        fn = f'{DATA_STORE}/{self.name}.csv'
        if os.path.isfile(fn):
            return self.or_fail(fn)
        # Infer to callback
        df = cb()
        df.to_csv(fn)
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
