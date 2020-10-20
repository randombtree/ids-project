#@title
# Seasonal anomalities
import re
import numpy as np
import pandas as pd
import datetime
import multiprocessing as mp
import matplotlib.image as mpimg

try:
    from config import config
    from lib import debug, open_url
    from lib.cache import open_cached, cached_name
    from lib.util import month_range
except ModuleNotFoundError:
    from ..config import config
    from ..lib import debug, open_url
    from ..lib.cache import open_cached, cached_name
    from ..lib.util import month_range

# All seasonal data is found under this URL
SEASONAL_BASE_URL = 'https://ies-ows.jrc.ec.europa.eu/SeasonalForecast'

# This is the approx coordinate of helsinki on the seasonal map
HELSINKI_COORD=(3841, 2117)

def RGB(val):
    if type(val) == str:
        m = re.match(r'([0-f]{2})([0-f]{2})([0-f]{2})', val)
        if not m:
            raise Exception(f'Unhandled RGB string {val}')
        # Convert hex str to int
        return tuple((int(s, 16) for s in m.groups()))
    else:
        raise Exception(f'Unhandled RGB type {type(val)}')

# Manual extraction of color-mappings (easiest w/ gimp and html notation)
TEMP_MAP={
    RGB('0000b0'): -3.5, # -4 - -3.5
    RGB('0024e0'): -3.0,
    RGB('0048ff'): -2.5,
    RGB('006cff'): -2.0,
    RGB('0090ff'): -1.5,
    RGB('00b4ff'): -1.0,
    RGB('00d8ff'): -0.5,
    RGB('00ffff'): -0.25,
    RGB('ffffff'): 0,
    RGB('ffe0a8'): 0.25,
    RGB('ffc090'): 0.5,
    RGB('ffa078'): 1.0,
    RGB('ff8060'): 1.5,
    RGB('ff6048'): 2.0,
    RGB('ff4030'): 2.5,
    RGB('e02018'): 3.0,
    RGB('b00000'): 3.5,
}

# Google colab does some strange things with the colors, so need to do color mappings
# on the fly; by reading the colors from the image first :(
# These are the coordinates where the color for a specific temp is located at in
# the map image

def generate_calibration_coords():
    """
    Generate list of tuples (row, col, temp) to be used when calibrating
    the mapping color -> temp
    """
    row = 770
    temps_minus = [-3.5, -3.0, -2.5, -2.0, -1.5, -1.0, -0.5, -0.25, 0]
    temps_plus =  [0.25, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5]
    tcoord_minus = [ (row, 472 + i * 288, t) for (t, i) in zip(temps_minus, range(len(temps_minus)))]
    tcoord_plus  = [ (row, 3522 + i * 288, t) for (t, i) in zip(temps_plus, range(len(temps_plus)))]
    return tcoord_minus + tcoord_plus

TEMP_CALIBRATION_COORDS = generate_calibration_coords()
def to_rgb(arr):
    """
    Extract rgb part of a rgba float array (ex. numpy.ndarray) to a hashable tuple
    """
    (r,g,b,a) = arr * 255
    return (int(r),int(g),int(b))

def get_temp_map(img):
    """
    Generates a dictionary with color -> temp mapping by reading predefined coordinates
    from the image.
    """
    return { to_rgb(img[row, col]): t for (row, col, t) in TEMP_CALIBRATION_COORDS }

def get_seasonal_temp_anomaly_from(fn):
    """
    Fetch the given filename from the repository and figure out the seasonal anomality temperature
    for Helsinki.
    """
    with open_url(f'{SEASONAL_BASE_URL}/{fn}', 'rb') as f:
        img = mpimg.imread(f)
        if img.shape != (4810, 6260, 4):
            raise Exception('Image shape has changed, must re-calibrate')

        tempmap = get_temp_map(img)
        rgb = to_rgb(img[HELSINKI_COORD[1], HELSINKI_COORD[0] ])
        if rgb in tempmap:
            return tempmap[rgb]
        if not rgb in tempmap:
            # Maps can have a gray border around differing temperature zones, fuzz around it before giving up
            for fuzz_x in range(1,21): # Borders are about size 10; so this should be enough (+-20)
                for fuzz_y in range(0,21):
                    # Search in all directions
                    for mult in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
                        rgb = to_rgb(img[HELSINKI_COORD[1] + (mult[0] * fuzz_x),
                                         HELSINKI_COORD[0] + (mult[1] * fuzz_y) ])
                        if rgb in tempmap:
                            return tempmap[rgb]
                        elif rgb in TEMP_MAP:
                            return TEMP_MAP[rgb]

        debug('Temperature not found in tempmap?')
        debug('Color map:',TEMP_MAP)
        if config.DEBUG:
            dbgname = 'debug_anomality_image.png'
            debug(f'Saving a copy of the problematic image as "{dbgname}"')
            mpimg.imsave(dbgname, img)

        raise Exception(f'Color {rgb} not found in mapping?')
    raise Exception('Fail')

RE_IMAGE = re.compile(r'^SeasonalAnomalies_T2m_(?P<date>\d+)_m(?P<n>\d)\.png')
CACHE_SEASONAL='cache_seasonal_anomalities'
def process_image(t):
    (d, n, fn) = t
    return (d, n, get_seasonal_temp_anomaly_from(fn))

def get_seasonal_anomalities():
    # Since it takes quite a while to generate this; it's only smart to cache it once done
    try:
        df = pd.read_json(open_cached(CACHE_SEASONAL))
        if config.DEBUG:
            debug('Returning cached seasonal data from', cached_name(CACHE_SEASONAL))
        return df
    except FileNotFoundError:
        # Ok, need to do the gathering
        pass

    # Text file containing file names for the temperature prognosis images
    # the format is 'SeasonalAnomalies_T2m_<YYYYMMDD>_m<N>.png' where Y, M, D are for the date and M is the month number
    # 1 = for the prognosis date month, e.g. for 20200901 N=1 and N7 is for march next year
    f = open_url(f'{SEASONAL_BASE_URL}/T2m_index.txt')
    lines = f.read().split('\n')
    lines.remove('') # Last entry
    anomalities = dict() # date -> list
    def image_data(fn):
        m = RE_IMAGE.match(fn)
        if m:
            day = datetime.datetime.strptime(m.group('date'), '%Y%m%d')
            n = int(m.group('n')) - 1 # indexing starts from 1 in file :/
            if not day in anomalities:
                anomalities[day] = [ np.NaN for _ in range(7) ]
            return (day, n, fn)

    # Run in parallel
    pool = mp.Pool()
    temps = pool.map(process_image,
                     [ image_data(fn) for fn in lines ])
    # Remap
    for (d,n,t) in temps:
        anomalities[d][n] = t
    df = pd.DataFrame([(k,) + tuple(v) for (k,v) in anomalities.items()],
                      columns = ['date'] + [f'month{n}' for n in range(7)])
    df.set_index('date', inplace = True)
    df.to_json(open_cached(CACHE_SEASONAL, mode='w'))
    return df

def anomalities_for(anomalities, index = -1):
    """
    Returns a DataFrame with the dates for the last (or index) anomality report.
    """
    row = anomalities.iloc[index]
    start_month = row.name
    df = pd.DataFrame(row)
    # Value row gets the index name - rename it
    df.rename(columns=lambda x: 'month' if len(x) == 0 else 'anomality', inplace = True)
    # Now need to rename indexes from "month0".. to start_month..
    new_index = list(month_range(row.name, 7))
    df.rename(index = lambda x: new_index[int(x[-1])], inplace = True)
    return df
