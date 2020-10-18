from flask import Flask, Response
import re
import pandas as pd

import data
import fetch_data

app = Flask(__name__)

print('Reading properties ...')
df_buildings = fetch_data.get_data('heated_buildings').or_fail()

@app.route('/')
def index():
    return 'Index Page'

@app.route('/hello')
def hello():
    return 'Hello, World'

@app.route('/api/properties')
def properties():
    return Response(
        df_buildings[['propertyName', 'latitude', 'longitude']].to_json(orient='index'),
        mimetype='application/json')

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    # Bundle return
    return 'You want path: %s' % path

