import pandas as pd
import numpy as np
import xml.etree.ElementTree as ET

try:
    from lib import open_url, debug
except ModuleNotFoundError:
    from ..lib import open_url, debug

def get_decade_temperatures():
    """
    Gather weather data for 2010-2020
    """
    ids = [101007, 101004, 100971, 100973]
    df = pd.DataFrame()
    for fmi_id in ids:
        days = []
        avg_temperatures = []
        for year in np.arange(2010, 2020, 1):
            with open_url(f'https://opendata.fmi.fi/wfs?request=getFeature&storedquery_id=fmi%3A%3Aobservations%3A%3Aweather%3A%3Adaily%3A%3Atimevaluepair&crs=EPSG%3A%3A3067&fmisid={fmi_id}&starttime={year}-01-01T00:00:00Z&endtime={year}-12-31T23:59:59Z', mode='rb') as fh:
                etree = ET.parse(fh)
                root = etree.getroot()
                try:
                    for child in root[1][0][6][0]:
                        days.append(child[0][0].text)
                        avg_temperatures.append(child[0][1].text)
                except:
                    pass

        temps = pd.DataFrame(list(zip(days, avg_temperatures)), columns=["date", "avg_temp"])
        temps[fmi_id] = temps["avg_temp"].astype("float")
        temps.drop("avg_temp", axis=1, inplace=True)
        temps["date"] = pd.to_datetime(temps["date"])
        temps["date"] = temps["date"].dt.date
        temps = temps.groupby([temps['date']])[fmi_id].mean()

        if df.shape[0] == 0:
            df = temps
        else:
            df = pd.merge(df,
                          temps,
                          how="outer",
                          left_index=True,
                          right_index=True)


    df["avg_temp"] = df.mean(axis=1)
    df.drop([101007, 101004, 100971, 100973], axis=1, inplace=True)
    df.index = pd.to_datetime(df.index)
    df = df.groupby(pd.Grouper(freq='M')).mean()

    #Set data for each month to be listed on first day of the month
    df.index = pd.to_datetime(df.reset_index()["date"].apply(lambda x: x.strftime('%Y-%m')))
    return df

