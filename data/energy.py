import pandas as pd
import numpy as np
import urllib.parse as urlparse
from scipy import stats
from sklearn import linear_model
import datetime
import pickle
import base64

try:
    from lib import open_url, debug
    from data.seasonal_anomalities import anomalities_for
    from lib.util import month_range
except ModuleNotFoundError:
    from ..lib import open_url, debug
    from ..data.seasonal_anomalities import anomalities_for
    from ..lib.util import month_range

ENERGY_RESOURCE = 'https://helsinki-openapi.nuuka.cloud/api/v1.0/EnergyData/Monthly/ListByProperty'
VALID_REPORTING_GROUPS = ['Electricity', 'Heat', 'Water', 'DistrictCooling']
def get_monthly_energy_data(buildingCode, reporting_group, start_time, end_time):
  """
  Reporting groups: 'Electricity', 'Heat', 'Water', 'DistrictCooling'
  throws: HTTPError if resource does not exist
  """

  if not reporting_group in VALID_REPORTING_GROUPS:
      raise ValueError(f'reporting_group should be one of {" ".join(VALID_REPORTING_GROUPS)}')
  resource = 'https://helsinki-openapi.nuuka.cloud/api/v1.0/EnergyData/Monthly/ListByProperty?Record=LocationName'

  params = urlparse.urlencode(
      { 'Record': 'BuildingCode',
        'SearchString': buildingCode,
        'ReportingGroup': reporting_group,
        'StartTime': start_time,
        'EndTime': end_time
      })
  search_url = f'{ENERGY_RESOURCE}?{params}'
  debug(f'Requesting {search_url}')
  ret = pd.read_json(open_url(search_url))
  return ret

def get_decade_heat_data(buildingCode):
    """
    Get 10 years of heat data for building.
    throws: HTTPError if resource does not exist
    """
    # Begin fetching from last month
    d = datetime.date.today()
    lastmonth = d - datetime.timedelta(days = d.day - 1)
    data = get_monthly_energy_data(buildingCode,
                                   'Heat',
                                   f'{lastmonth.year - 10}-{lastmonth.month}-01',
                                   lastmonth.strftime('%Y-%m-%d')) # Unsure if ranges are inclusive or exclusive
    data["date"] = pd.to_datetime(data["timestamp"])
    #Set data for each month to be listed on first day of the month
    data["date"] = pd.to_datetime(data["date"].apply(lambda x: x.strftime('%Y-%m')))
    data.set_index("date", inplace=True)
    data.drop(["timestamp", "reportingGroup", "locationName", "unit"], axis=1, inplace=True)
    #Drop extreme outliers. We need might need to loop a few times, because some outliers are so big they make other outliers look normal 
    while (np.abs(stats.zscore(data)) >= 6).any():
        data = data[(np.abs(stats.zscore(data)) < 6).all(axis=1)]
    return data

def generate_heating_models(properties_df, temp_df):

    def make_model(row):
        """
        Construct model(s) for building at row
        """
        building = row.name # Indexing by buildingName
        try:
            building_heat_df = get_decade_heat_data(building)
        except IOError as e:
            # Building has no heating data
            debug(f'{building} lacks data')
            return None
        # Record starting & stop date
        # these can then be used for example with df.columns.get_loc(row['heating_start'])
        # to get the column indexes that contain data or just calculate the dates manually
        heating_start = str(building_heat_df.iloc[0].name)[:10]
        heating_stop  = str(building_heat_df.iloc[-1].name)[:10]
        #Merge df:s to make inner join
        building_df = pd.merge(building_heat_df,
                               temp_df["avg_temp"],
                               left_index=True,
                               right_index=True)
        building_df.dropna(inplace = True)
        if not building_df.shape[0]:
            # No data
            return None
        lin_m = linear_model.LinearRegression()
        log_m = linear_model.LinearRegression()

        X = building_df["avg_temp"].values.reshape(-1, 1)
        lin_Y = building_df["value"].values.reshape(-1, 1)
        #Add a tiny amount to fix log(0)
        log_Y = np.log(lin_Y + 3)

        lin_m.fit(X, lin_Y)
        log_m.fit(X, log_Y)
        d = {
            'datapoints':    building_df.shape[0],
            'lin_score':     lin_m.score(X, lin_Y),
            'lin_coef':      lin_m.coef_[0][0],
            'lin_intercept': lin_m.intercept_[0],
            'lin_model':     base64.b64encode(pickle.dumps(lin_m)).decode(), # Need to keep as regular str
            'log_score':     log_m.score(X, log_Y),
            'log_coef':      log_m.coef_[0][0],
            'log_intercept': log_m.intercept_[0],
            'log_model':     base64.b64encode(pickle.dumps(log_m)).decode(),
            'heating_start': heating_start,
            'heating_stop':  heating_stop,
        }
        # Add the monthly heating data
        for i, v in building_heat_df.iterrows():
            d[str(i)[:10]] = v.value
        return pd.Series(d)

    return properties_df.apply(make_model, axis=1)

def unthaw(s):
    return pickle.loads(base64.b64decode(s))

def make_prognosis(building, avg_df, anomalities_df):
    """
    Make prognosis on building energy consumtion, when served with the
    average temperature and the latest temperature anomalities.
    """
    df = anomalities_for(anomalities_df)
    df['month'] = df.index.str[5:7].astype(int)
    df2 = df.merge(how='left', right = avg_df, left_on = 'month', right_index = True)
    df2['predicted_temp'] = df2.anomality + df2.avg_temp
    # Choose the best model
    model = unthaw(building.lin_model) if building.lin_score > building.log_score else unthaw(building.log_model)
    prediction = model.predict(df2.predicted_temp.values.reshape(-1, 1))
    return pd.DataFrame(
        prediction,
        index = df.index,
        columns = ['heating']
    )

