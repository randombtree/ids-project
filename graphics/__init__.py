import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from lib.util import month_range

def plot_energy_temperature_history(building, temp_df, prognosis_df, out):
    """
    Plots the energy vs. temperature inverse graph.
    """
    heat_data = building[list(month_range(building.heating_start, building.heating_stop))]
    df = pd.merge(heat_data, temp_df["avg_temp"], left_index=True, right_index=True)
    # Now to fill the dots in between if data has holes in the end
    for d in month_range(building.heating_stop, prognosis_df.index[-1]):
        if not d in df.index:
            df.loc[d] = np.nan
    # Add prognosis
    df = df.merge(right = prognosis_df, left_index = True, right_index = True, how = 'left')
    # The query results in some random column name for heat values, fix it:
    df.rename(columns={heat_data.name: 'value'}, inplace = True)
    # Change to datetime
    df.rename(index = lambda s: pd.to_datetime(s))
    fig, ax = plt.subplots(figsize=(5,4))
    # Heating actualized
    ax.plot(df["value"], 'r-')
    ax.set_ylabel("Heat energy usage by month, KWh")
    ax.legend("Energy", loc="upper left")
    # Prognosis
    ax.plot(df.heating, 'r:')
    # Temperatures
    ax2 = ax.twinx()
    plt.gca().invert_yaxis()
    ax2.plot(df["avg_temp"], 'g-', alpha=0.7)
    ax2.set_ylabel("Average temperature, °C")
    ax2.legend("Temp (inv)")
    plt.savefig(out)
