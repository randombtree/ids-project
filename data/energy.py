import pandas as pd
import numpy as np
import urllib.parse as urlparse
from scipy import stats
from sklearn import linear_model

try:
    from lib import open_url, debug
except ModuleNotFoundError:
    from ..lib import open_url, debug

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
  ret = pd.read_json(open_url(search_url))
  return ret

def get_decade_heat_data(buildingCode):
    """
    Get 10 years of heat data for building.
    throws: HTTPError if resource does not exist
    """

    data = get_monthly_energy_data(buildingCode, 'Heat', '2010-01-01', '2020-01-01')
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
        return pd.Series({
            'datapoints':    building_df.shape[0],
            'lin_score':     lin_m.score(X, lin_Y),
            'lin_coef':      lin_m.coef_[0][0],
            'lin_intercept': lin_m.intercept_[0],
            'log_score':     log_m.score(X, log_Y),
            'log_coef':      log_m.coef_[0][0],
            'log_intercept': log_m.intercept_[0],
            })

    return properties_df.apply(make_model, axis=1)
