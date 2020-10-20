import pandas as pd
import numpy as np
import xml.etree.ElementTree as ET
import datetime

try:
    from lib import open_url, debug
except ModuleNotFoundError:
    from ..lib import open_url, debug

def get_decade_temperatures():
    """
    Gather weather data for 2010-now
    """
    ids = [101007, 101004, 100971, 100973]
    df = pd.DataFrame()
    for fmi_id in ids:
        days = []
        avg_temperatures = []
        today = datetime.date.today()
        for year in range(2010, today.year + 1):
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

def get_monthly_averages(temp_df):
    """
    Return average temperatures per month for temp_df,
    which is expected to be in the format provided by get_decade_temperatures()
    """
    avgs = list((0,0) for _ in range(0,12)) # (count, sum) for each month
    for index, row in temp_df.iterrows():
        month = int(index[5:7]) - 1
        counts = avgs[month]
        temp = row.avg_temp + 273 # Kelvin-ish
        avgs[month] = (counts[0] + 1, counts[1] + temp)
    # Calculate averages
    avgs = list(map(lambda i: (i[1] / i[0]) - 273, avgs))
    return pd.DataFrame(avgs, index = range(1,13), columns=['avg_temp'])
