import pandas as pd
import urllib.parse as urlparse
from scipy import stats

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

