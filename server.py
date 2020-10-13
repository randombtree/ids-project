from flask import Flask, Response
import re
import pandas as pd

import data


app = Flask(__name__)

print('Fetching properties ...')
df_properties = data.get_properties()

# This should probably go into get_properties, buf for now.. :

# Convert lat & lng to numeric
coordRe = re.compile(r'^\d+(\.\d+)?$')
def fixLatLng(col):
    if col.name in ['latitude', 'longitude']:
        # Missing or invalid values will be converted to NaN and cand be later dropped
        return pd.to_numeric(col, errors = 'coerce')
    return col
df_properties = df_properties.apply(fixLatLng)
# Drop NaN coordinates
df_properties.dropna(inplace = True)


@app.route('/')
def index():
    return 'Index Page'

@app.route('/hello')
def hello():
    return 'Hello, World'

@app.route('/api/properties')
def properties():
    return Response(
        df_properties[['propertyName', 'latitude', 'longitude']].to_json(orient='records'),
        mimetype='application/json')

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    # Bundle return
    return 'You want path: %s' % path

