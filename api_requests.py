import requests
import pickle
import re
import pandas as pd
import datetime as dt
from bs4 import BeautifulSoup as bs
from ignore import GEO_API, ELE_API, tz, tz_s


def first_try():
    global latitude, longitude, elevation
    ft = True
    try:
        with open('loc.dat', 'rb') as file:
            latitude, longitude, elevation = pickle.load(file)
    except FileNotFoundError:
        ft = False
    finally:
        return ft


def position_recall():
    global df, phase
    _ = None
    try:
        with open('current.dat', 'rb') as file:
            df, phase, _ = pickle.load(file)
    except FileNotFoundError:
        api_request()
        with open('current.dat', 'rb') as file:
            df, phase, _ = pickle.load(file)
    finally:
        lag = dt.datetime.now() - _
        if lag.seconds > 21600:
            api_request()
    return [df, phase]


def api_request(soup=True):
    global df, phase, latitude, longitude, elevation
    response = requests.get(
        f'https://api.visibleplanets.dev/v3?latitude={latitude}&longitude={longitude}&elevation={elevation}&aboveHorizon=false')
    if response.status_code == 200:
        df_data = {i['name']: [i['constellation'], [i['altitude'], i['azimuth']], True if i['altitude'] > 0 else False]
                   for i in response.json()['data'] if i['nakedEyeObject'] is True}
        if soup:
            df_data = rise_set(df_data)
            df = pd.DataFrame(df_data)
        else:
            df2 = pd.DataFrame(df_data)
            df.loc[[0, 1, 2]] = df2.loc[[0, 1, 2]]
            return df
        phase = response.json()['data'][1]['phase']
        with open('current.dat', 'wb') as file:
            pickle.dump([df, phase, dt.datetime.now()], file)


def re_location(address):
    global GEO_API, ELE_API
    url = 'https://map-geocoding.p.rapidapi.com/json'
    query = {'address': address}
    response = requests.get(url, headers=GEO_API, params=query).json()['results'][0]['geometry']
    lat, lng = response['location']['lat'], response['location']['lng']
    url = "https://elevation-from-latitude-and-longitude.p.rapidapi.com/"
    query = {'lat': f'{lat}', 'lng': f'{lng}'}
    elevation = requests.get(url, headers=ELE_API, params=query).json()['elevation']
    location_set([lat, lng, elevation])


def location_set(info):
    global latitude, longitude, elevation
    latitude, longitude, elevation = info
    with open('loc.dat', 'wb') as file:
        pickle.dump([latitude, longitude, elevation], file)


def rise_set(df_data):
    planets = {
        'Sun': 10,
        'Moon': 11,
        'Mercury': 1,
        'Venus': 2,
        'Mars': 4,
        'Jupiter': 5,
        'Saturn': 6
    }
    non_vis = {}
    for i in planets.keys():
        date = dt.date.today().strftime('%Y-%m-%d')
        url = f'''
        https://aa.usno.navy.mil/calculated/mrst?body={planets[i]}&date={date}&reps=1&lat={latitude}&lon=
        {longitude}&label=&tz={tz}&tz_sign={tz_s}&height={elevation}&submit=Get+Data'''
        response = requests.get(url)
        soup = bs(response.text, 'html.parser')
        soup = str(soup.find_all('pre'))
        for g in soup.splitlines():
            if g.startswith(dt.date.today().strftime('%Y')):
                riset = re.findall(r'\d{2}:\d{2}', g)
        if i != 'Sun':
            riset.remove(riset[1])
        else:
            riset = [riset[1], riset[3]]
        df_data[i].append(riset)
    return df_data
