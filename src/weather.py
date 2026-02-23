"""
Weather data — Open-Meteo Historical Weather API.

Free, no API key, no registration required.
One API call fetches the entire date range (e.g., 2 full years).
Response is cached to disk so re-runs are instant.

API reference: https://open-meteo.com/en/docs/historical-weather-api
Archive endpoint: https://archive-api.open-meteo.com/v1/archive
"""

import os
import json
import random
from datetime import datetime, date, timedelta
from collections import defaultdict, Counter

import requests

# ---------------------------------------------------------------------------
# WMO Weather Interpretation Codes → readable condition
# https://open-meteo.com/en/docs#weathervariables
# ---------------------------------------------------------------------------

WMO_TO_CONDITION = {
    0:  'Clear',                          # Clear sky
    1:  'Clear',                          # Mainly clear
    2:  'Clouds',                         # Partly cloudy
    3:  'Clouds',                         # Overcast
    45: 'Fog',    48: 'Fog',             # Fog / rime fog
    51: 'Rain',   53: 'Rain',   55: 'Rain',   # Drizzle
    56: 'Rain',   57: 'Rain',             # Freezing drizzle
    61: 'Rain',   63: 'Rain',   65: 'Rain',   # Rain
    66: 'Rain',   67: 'Rain',             # Freezing rain
    71: 'Snow',   73: 'Snow',   75: 'Snow',   # Snowfall
    77: 'Snow',                           # Snow grains
    80: 'Rain',   81: 'Rain',   82: 'Rain',   # Rain showers
    85: 'Snow',   86: 'Snow',             # Snow showers
    95: 'Thunderstorm',
    96: 'Thunderstorm', 99: 'Thunderstorm',
}


def _wmo_to_condition(code):
    """Map a WMO weather code integer to a human-readable condition string."""
    if code is None:
        return 'Clouds'
    return WMO_TO_CONDITION.get(int(code), 'Clouds')


# ---------------------------------------------------------------------------
# Open-Meteo fetch + cache
# ---------------------------------------------------------------------------

def fetch_openmeteo(lat: float, lon: float,
                    start_date: date, end_date: date,
                    cache_dir: str = 'data/weather_cache') -> dict:
    """
    Fetch hourly historical weather from Open-Meteo for a full date range.

    - Free, no API key required.
    - One HTTP call covers any date range.
    - Raw JSON is cached to disk; subsequent calls are instant.

    Returns the raw API response dict.
    """
    os.makedirs(cache_dir, exist_ok=True)

    cache_name = f"openmeteo_{lat}_{lon}_{start_date}_{end_date}.json"
    cache_path = os.path.join(cache_dir, cache_name)

    if os.path.exists(cache_path):
        print(f"  Weather: loaded from cache ({cache_name})")
        with open(cache_path, 'r') as f:
            return json.load(f)

    print(f"  Weather: fetching from Open-Meteo ({start_date} → {end_date}) ...")

    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        'latitude':   lat,
        'longitude':  lon,
        'start_date': str(start_date),
        'end_date':   str(end_date),
        'hourly':     'temperature_2m,relative_humidity_2m,precipitation,weathercode,windspeed_10m',
        'timezone':   'Europe/Ljubljana',
    }

    response = requests.get(url, params=params, timeout=60)
    response.raise_for_status()
    data = response.json()

    with open(cache_path, 'w') as f:
        json.dump(data, f)

    n_hours = len(data.get('hourly', {}).get('time', []))
    print(f"  Weather: {n_hours} hourly records fetched and cached.")
    return data


def parse_daily_summaries(raw_data: dict, location_id: int) -> list:
    """
    Aggregate Open-Meteo hourly data into one record per day.

    Daily values:
      temperature   = average of all 24 hourly readings (°C)
      precipitation = total mm for the day
      conditions    = most common WMO condition for the day
      wind_speed    = daily average (m/s)
      humidity      = daily average (%)

    Returns list of dicts suitable for bulk_insert_mappings → WeatherSnapshot.
    """
    hourly = raw_data['hourly']
    times   = hourly['time']                    # "2023-01-01T00:00"
    temps   = hourly['temperature_2m']
    humids  = hourly.get('relative_humidity_2m', [None] * len(times))
    precips = hourly['precipitation']
    codes   = hourly['weathercode']
    winds   = hourly['windspeed_10m']

    by_day = defaultdict(lambda: {
        'temps': [], 'humids': [], 'precips': [], 'codes': [], 'winds': []
    })

    for i, t in enumerate(times):
        day = t[:10]   # "2023-01-01"
        v = by_day[day]
        v['temps'].append(temps[i]   if temps[i]   is not None else 10.0)
        v['humids'].append(humids[i] if humids[i]  is not None else 70)
        v['precips'].append(precips[i] if precips[i] is not None else 0.0)
        v['codes'].append(int(codes[i]) if codes[i] is not None else 2)
        v['winds'].append(winds[i]   if winds[i]   is not None else 2.0)

    records = []
    for day_str in sorted(by_day.keys()):
        v = by_day[day_str]
        d = date.fromisoformat(day_str)
        dominant_code = Counter(v['codes']).most_common(1)[0][0]

        records.append({
            'location_id':   location_id,
            'timestamp':     datetime(d.year, d.month, d.day, 12, 0, 0),
            'temperature':   round(sum(v['temps'])   / len(v['temps']),   1),
            'precipitation': round(sum(v['precips']),                     1),
            'conditions':    _wmo_to_condition(dominant_code),
            'wind_speed':    round(sum(v['winds'])   / len(v['winds']),   1),
            'humidity':      int(sum(v['humids'])    / len(v['humids'])),
            'source':        'open-meteo',
        })

    return records


def fetch_and_store_weather(session, location,
                             start_date: date, end_date: date):
    """
    Main entry point. Fetches real weather from Open-Meteo and inserts
    into the weather_snapshots table.

    Falls back to synthetic Ljubljana data if the API is unreachable.
    """
    from src.db_models import WeatherSnapshot

    try:
        raw = fetch_openmeteo(location.latitude, location.longitude,
                              start_date, end_date)
        records = parse_daily_summaries(raw, location.id)
        session.bulk_insert_mappings(WeatherSnapshot, records)
        session.flush()
        print(f"  Stored {len(records)} daily weather records (source: open-meteo)")

    except Exception as e:
        print(f"  Open-Meteo unavailable ({e}). Falling back to synthetic weather ...")
        _store_synthetic(session, location, start_date, end_date)


# ---------------------------------------------------------------------------
# Synthetic fallback — realistic Ljubljana climate averages (ARSO data)
# Used only if Open-Meteo API is unreachable.
# ---------------------------------------------------------------------------

# month: (avg_temp_C, temp_std, condition_weights)
# condition_weights order: [Clear, Clouds, Rain, Snow, Fog, Thunderstorm]
_CLIMATE = {
    1:  (-1, 5, [15, 35, 25, 15, 10,  0]),
    2:  ( 2, 5, [20, 35, 25, 10, 10,  0]),
    3:  ( 7, 5, [25, 35, 30,  5,  5,  0]),
    4:  (12, 4, [25, 30, 40,  0,  5,  0]),
    5:  (17, 4, [30, 25, 35,  0,  5,  5]),
    6:  (21, 3, [35, 25, 25,  0,  5, 10]),
    7:  (24, 3, [45, 25, 20,  0,  0, 10]),
    8:  (24, 3, [40, 25, 20,  0,  0, 15]),
    9:  (19, 4, [30, 30, 30,  0,  5,  5]),
    10: (12, 4, [20, 35, 35,  0, 10,  0]),
    11: ( 5, 4, [15, 35, 30,  5, 15,  0]),
    12: ( 1, 5, [15, 35, 25, 10, 15,  0]),
}
_COND_LABELS = ['Clear', 'Clouds', 'Rain', 'Snow', 'Fog', 'Thunderstorm']


def _store_synthetic(session, location, start_date: date, end_date: date):
    from src.db_models import WeatherSnapshot

    records = []
    cur = start_date
    while cur <= end_date:
        avg_t, std_t, cond_w = _CLIMATE[cur.month]
        cond = random.choices(_COND_LABELS, weights=cond_w, k=1)[0]
        precip = 0.0
        if cond in ('Rain', 'Thunderstorm'):
            precip = round(random.uniform(0.5, 15.0), 1)
        elif cond == 'Snow':
            precip = round(random.uniform(0.5, 5.0), 1)

        records.append({
            'location_id':   location.id,
            'timestamp':     datetime(cur.year, cur.month, cur.day, 12, 0, 0),
            'temperature':   round(random.gauss(avg_t, std_t), 1),
            'precipitation': precip,
            'conditions':    cond,
            'wind_speed':    round(random.uniform(0.5, 6.0), 1),
            'humidity':      random.randint(55, 95),
            'source':        'synthetic',
        })
        cur += timedelta(days=1)

    session.bulk_insert_mappings(WeatherSnapshot, records)
    session.flush()
    print(f"  Stored {len(records)} synthetic weather records (fallback)")
