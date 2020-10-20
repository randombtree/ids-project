import pandas as pd
import numpy as np
import matplotlib.dates as mdates
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import datetime

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
    df.rename(index = lambda s: datetime.datetime.fromisoformat(s), inplace = True)
    fig = Figure()
    canvas = FigureCanvas(fig)
    ax = fig.add_subplot(111)
    # Heating actualized
    ax.plot(df["value"], 'r-')
    ax.set_ylabel("Heat energy usage by month, KWh")
    ax.legend("Energy", loc="upper left")
    # Prognosis
    ax.plot(df.heating, 'r:')
    # Set year formatting
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax.xaxis.set_minor_locator(mdates.MonthLocator())

    # Temperatures
    ax2 = ax.twinx()
    fig.gca().invert_yaxis()
    ax2.plot(df["avg_temp"], 'g-', alpha=0.7)
    ax2.set_ylabel("Average temperature, °C")
    ax2.legend("Temp (inv)")

    fig.tight_layout()
    fig.autofmt_xdate()
    fig.savefig(out)
