import pandas as pd
import numpy as np
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

def extract_primary_building(s):
    """
    Extract the first building code; currently we are not using other than the
    'primary' building, but later on this could change..
    """
    d = {}
    if len(s) >= 1:
        b = s[0]
        d['buildingCode'] = b['buildingCode']
    return d

def get_properties():
    """
    Fetch all properties with data.
    """
    properties = get_property_list()
    properties_df =  pd.concat(list(fetchPropDataGenerator(properties)))

    buildingCode = properties_df.buildings.apply(
        lambda s: pd.Series(extract_primary_building(s), dtype=np.object))
    # Drop fields we currently don't use
    properties_df.drop(['yearOfIntroduction',
                        'purposeOfUse',
                        'buildingType',
                        'buildings'],
                       axis = 1, inplace = True)
    df =  pd.concat([properties_df, buildingCode], axis = 1)
    # Need to have a unique index for the drop to work properly
    df.reset_index(drop = True, inplace = True)
    # Remove properties that have no building code
    df.drop(df[df['buildingCode'].isna()].index, inplace = True)
    df.set_index('buildingCode', inplace = True)
    return df
