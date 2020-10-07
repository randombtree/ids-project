import pandas as pd

from ..lib import open_url

def get_properties():
    return pd.read_json(open_url('https://helsinki-openapi.nuuka.cloud/api/v1.0/Property/List',
                                 mode='rb'))
