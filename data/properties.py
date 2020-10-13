import pandas as pd
import urllib.parse as urlparse

try:
    from lib import open_url, debug
except ModuleNotFoundError:
    from ..lib import open_url, debug

def get_property_list():
    """
    Fetches the 'densified' property list only containing name and code
    """
    return pd.read_json(open_url('https://helsinki-openapi.nuuka.cloud/api/v1.0/Property/List',
                                 mode='rb'))

PROPERTY_RESOURCE = 'https://helsinki-openapi.nuuka.cloud/api/v1.0/Property/Search'
def fetchPropData(row):
    """
    Fetches one property data row.
    Throws IOError (HTTPError) if data not found.
    """
    params = urlparse.urlencode(
        { 'SearchFromRecord': 'PropertyCode',
          'SearchString': row['propertyCode'] })
    search_url = f'{PROPERTY_RESOURCE}?{params}'
    ret = pd.read_json(open_url(search_url))
    return ret

def fetchPropDataGenerator(props_df):
    """
    A generator that returns (yields) all valid properties row by row.
    """
    for index, row in props_df.iterrows():
        try:
            # There are some properties missing property codes :/
            code = row['propertyCode']
            # Missing data
            if not code:
                code = ''

            code = code.strip()
            if code != '':
                yield fetchPropData(row)
            else:
                debug('Missing property code:', row )
        except IOError:
            # Some properties return 404 :)
            debug('Not found: ', code)
            pass

def get_properties():
    """
    Fetch all properties with data.
    """
    properties = get_property_list()
    return pd.concat(list(fetchPropDataGenerator(properties)))
