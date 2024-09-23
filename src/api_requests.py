import requests
import pickle
import time
import re
import pandas as pd
import datetime as dt
from bs4 import BeautifulSoup as BS

tz = int(time.timezone /3600)
tz_s = -1

def first_try():
    """
    Attempts to load location data from a local file. If the file is not found, 
    it returns True to indicate that the location setup is needed.
    
    Returns:
        bool: True if location setup is needed, False otherwise.
    """
    global latitude, longitude, elevation, GEO_API, ELE_API
    ft = False
    try:
        # Attempt to load location data from a file
        with open('loc.dat', 'rb') as file:
            latitude, longitude, elevation = pickle.load(file)
        with open('../Data/keys.dat', 'rb') as file:
            GEO_API, ELE_API = pickle.load(file)
    except FileNotFoundError:
        ft = True
    finally:
        return ft

def position_recall():
    """
    Retrieves planetary position data from a local file or makes an API request if the data is outdated.
    
    Returns:
        list: A list containing the position data and phase information.
    """
    global df, phase, _
    _ = None
    try:
        # Load position data from the file
        with open('current.dat', 'rb') as file:
            df, phase, _ = pickle.load(file)
    except FileNotFoundError:
        # Make API request if file is not found
        api_request()
        with open('current.dat', 'rb') as file:
            df, phase, _ = pickle.load(file)
    finally:
        lag = dt.datetime.now() - _
        # Refresh data if older than 6 hours
        if lag.seconds > 21600:
            api_request()
    return [df, phase]

def api_request(soup=True):
    """
    Makes an API request to retrieve current planetary data and stores it locally.
    
    Args:
        soup (bool): Whether or not to retrieve rise and set times.
    """
    global df, phase, _, latitude, longitude, elevation
    lag = dt.datetime.now() - _
    if lag.seconds < 43200:
        soup = False
    # Make API request for planetary data
    response = requests.get(
        f'https://api.visibleplanets.dev/v3?latitude={latitude}&longitude={longitude}&elevation={elevation}&aboveHorizon=false')
    if response.status_code == 200:
        # Parse API response into a data structure
        df_data = {i['name']: [i['constellation'], [i['altitude'], i['azimuth']], True if i['altitude'] > 0 else False]
                   for i in response.json()['data'] if i['nakedEyeObject'] is True}
        if soup:
            # If soup is true, get rise and set times
            df_data = rise_set(df_data)
            df = pd.DataFrame(df_data)
        else:
            df2 = pd.DataFrame(df_data)
            df.loc[[0, 1, 2]] = df2.loc[[0, 1, 2]]
        phase = response.json()['data'][1]['phase']
        # Save the data locally
        with open('current.dat', 'wb') as file:
            pickle.dump([df, phase, dt.datetime.now()], file)

def re_location(address):
    """
    Updates the latitude, longitude, and elevation information based on a provided address.
    
    Args:
        address (str): The address to use for determining the location.
    """
    global GEO_API, ELE_API
    with open('../Data/keys.dat', 'rb') as file:
        GEO_API, ELE_API = pickle.load(file)
    # Get geolocation data from the address
    url = 'https://map-geocoding.p.rapidapi.com/json'
    query = {'address': address}
    response = requests.get(url, headers=GEO_API, params=query).json()['results'][0]['geometry']
    lat, lng = response['location']['lat'], response['location']['lng']
    # Get elevation data for the location
    url = "https://elevation-from-latitude-and-longitude.p.rapidapi.com/"
    query = {'lat': f'{lat}', 'lng': f'{lng}'}
    elevation = requests.get(url, headers=ELE_API, params=query).json()['elevation']
    location_set([lat, lng, elevation])

def location_set(info):
    """
    Stores the location data locally in a file.
    
    Args:
        info (list): The latitude, longitude, and elevation data to save.
    """
    global latitude, longitude, elevation
    latitude, longitude, elevation = info
    with open('loc.dat', 'wb') as file:
        pickle.dump([latitude, longitude, elevation], file)

def rise_set(df_data):
    """
    Adds rise and set times to the planetary data.
    
    Args:
        df_data (dict): The dictionary of planetary data that will have rise and set times added.
    
    Returns:
        dict: The updated dictionary with rise and set times included.
    """
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
        soup = BS(response.text, 'html.parser')
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
