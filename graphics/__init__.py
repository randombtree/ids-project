import pandas as pd
import matplotlib.pyplot as plt

from lib.util import month_range

def plot_energy_temperature_history(building, temp_df, prognosis_df, out):
    """
    Plots the energy vs. temperature inverse graph.
    """
    heat_data = building[list(month_range(building.heating_start, building.heating_stop))]
    df = pd.merge(heat_data, temp_df["avg_temp"], left_index=True, right_index=True)
    df = pd.concat([df, prognosis_df])
    # The query results in some random column name for heat values, fix it:
    df.rename(columns={heat_data.name: 'value'}, inplace = True)
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
