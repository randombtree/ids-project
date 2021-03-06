from flask import Flask, Response, abort, send_file
import io

import graphics
from data.wrangler import get_data
from data.energy import make_prognosis

app = Flask(__name__, static_folder = 'build/static')

print('Reading properties ...')
df_buildings = get_data('heated_buildings').or_fail()
df_temperatures = get_data('decade_temperatures').or_fail()
df_avgtemp = get_data('avg_temperatures').or_fail()
df_anomalities = get_data('seasonal_anomalities').or_fail()

@app.route('/api/properties')
def properties():
    return Response(
        df_buildings[['propertyName', 'latitude', 'longitude']].to_json(orient='index'),
        mimetype='application/json')

@app.route('/api/properties/<building>/energy_history')
def energy_history(building):
    if not building in df_buildings.index:
        abort(404)
    row = df_buildings.loc[building]
    prognosis = make_prognosis(row, df_avgtemp, df_anomalities)
    # Store image in memory
    buf = io.BytesIO()
    graphics.plot_energy_temperature_history(row, df_temperatures, prognosis, buf)
    buf.seek(0)
    return send_file(buf, mimetype='image/png')

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    return send_file('build/index.html')

