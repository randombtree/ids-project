import pandas as pd
import urllib.parse as urlparse

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
