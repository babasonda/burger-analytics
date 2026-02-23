"""
Bun demand prediction model.

What it does:
  Looks at 4 years of historical data (day of week, month, weather) and
  learns the pattern. Then predicts how many burgers will be sold tomorrow
  so the restaurant orders exactly the right number of buns.

Model: Random Forest Regressor (scikit-learn)
  Why Random Forest?
  - Handles non-linear patterns well (weather only matters above/below thresholds)
  - No need to scale or normalise the data
  - Gives feature importance — you can show the client "weather accounts for X% of the prediction"
  - Fast to train on small datasets (4 years of daily data = ~1460 rows)
  - Better than linear regression for this kind of mixed categorical + numeric data

Train/test split: temporal — train on first 3 years, test on last full year.
Never train on future data (that would be cheating and give fake accuracy numbers).
"""

import os
import json

import numpy as np
import pandas as pd
import requests
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error

from src.weather import _wmo_to_condition

# ---------------------------------------------------------------------------
# Feature definitions
# ---------------------------------------------------------------------------

FEATURES = [
    'day_of_week',    # 0 = Monday … 6 = Sunday
    'month',          # 1–12 — captures seasonality
    'year',           # captures the growth trend over years
    'is_weekend',     # 1 if Saturday or Sunday
    'temperature',    # daily average °C
    'precipitation',  # daily total mm
    'is_rain',        # 1 if precipitation > 1mm (binary flag for the -20% effect)
    'is_hot_sunny',   # 1 if temp > 25°C (binary flag for the +15% terrace effect)
]

TARGET = 'actual_buns_used'   # what we are predicting = burgers sold that day


# ---------------------------------------------------------------------------
# Feature engineering
# ---------------------------------------------------------------------------

def prepare_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add model features to a DataFrame that has at minimum:
      - 'day' (datetime)
      - 'temperature' (float, daily avg °C)
      - 'precipitation' (float, daily mm)

    Returns the same DataFrame with FEATURES columns added.
    """
    df = df.copy()
    df['day'] = pd.to_datetime(df['day'])

    df['day_of_week'] = df['day'].dt.dayofweek
    df['month']       = df['day'].dt.month
    df['year']        = df['day'].dt.year
    df['is_weekend']  = (df['day_of_week'] >= 5).astype(int)

    # Fill missing weather with median (edge case for very recent dates)
    df['temperature']  = df['temperature'].fillna(df['temperature'].median())
    df['precipitation'] = df['precipitation'].fillna(0.0)

    df['is_rain']      = (df['precipitation'] > 1.0).astype(int)
    df['is_hot_sunny'] = (df['temperature'] > 25.0).astype(int)

    return df


# ---------------------------------------------------------------------------
# Model training
# ---------------------------------------------------------------------------

def train_model(df_train: pd.DataFrame) -> RandomForestRegressor:
    """
    Train a Random Forest on historical daily data.

    df_train must have FEATURES columns + 'actual_buns_used' as the target.
    Returns a fitted model ready to call .predict() on.
    """
    X = df_train[FEATURES]
    y = df_train[TARGET]

    model = RandomForestRegressor(
        n_estimators=300,    # number of trees — more = more stable, diminishing returns after ~300
        max_depth=8,         # how deep each tree goes — prevents overfitting
        min_samples_leaf=5,  # each leaf needs at least 5 days — prevents memorising outliers
        random_state=42,     # fixed seed so results are reproducible
        n_jobs=-1,           # use all CPU cores
    )
    model.fit(X, y)
    return model


# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------

def evaluate_model(model: RandomForestRegressor, df_test: pd.DataFrame) -> dict:
    """
    Evaluate the model on unseen test data.

    Returns a dict with:
      mae          — mean absolute error in buns (e.g. "off by 18 buns on average")
      mape         — mean absolute % error (e.g. "off by 5% on average")
      df_results   — DataFrame with date, actual, predicted, error columns
    """
    X_test  = df_test[FEATURES]
    y_test  = df_test[TARGET].values
    y_pred  = model.predict(X_test).round().astype(int)

    mae  = mean_absolute_error(y_test, y_pred)
    mape = float((np.abs(y_test - y_pred) / y_test * 100).mean())

    df_results = pd.DataFrame({
        'day':       df_test['day'].values,
        'actual':    y_test,
        'predicted': y_pred,
        'error':     y_pred - y_test,          # positive = over-ordered, negative = under
        'error_pct': ((y_pred - y_test) / y_test * 100).round(1),
    })

    return {
        'mae':        round(mae, 1),
        'mape':       round(mape, 1),
        'df_results': df_results,
    }


def get_feature_importance(model: RandomForestRegressor) -> pd.DataFrame:
    """
    Returns a DataFrame showing how much each feature contributed to predictions.
    Higher = more important for the model.
    """
    return (
        pd.DataFrame({'feature': FEATURES, 'importance': model.feature_importances_})
        .sort_values('importance', ascending=True)   # ascending for horizontal bar chart
    )


# ---------------------------------------------------------------------------
# 7-day forecast from Open-Meteo (free, no API key)
# ---------------------------------------------------------------------------

def fetch_weather_forecast(lat: float, lon: float,
                            cache_dir: str = 'data/weather_cache') -> pd.DataFrame:
    """
    Fetch the next 7 days of weather forecast from Open-Meteo.
    Free, no API key needed. Result cached for today (one fetch per day).

    Returns DataFrame with: day, temperature, precipitation, conditions.
    """
    os.makedirs(cache_dir, exist_ok=True)
    today = pd.Timestamp.today().date()
    cache_path = os.path.join(cache_dir, f'forecast_{lat}_{lon}_{today}.json')

    if os.path.exists(cache_path):
        with open(cache_path, 'r') as f:
            data = json.load(f)
    else:
        url = 'https://api.open-meteo.com/v1/forecast'
        params = {
            'latitude':      lat,
            'longitude':     lon,
            'daily': 'temperature_2m_max,temperature_2m_min,precipitation_sum,weathercode',
            'timezone':      'Europe/Ljubljana',
            'forecast_days': 7,
        }
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        with open(cache_path, 'w') as f:
            json.dump(data, f)

    d = data['daily']
    df = pd.DataFrame({
        'day': pd.to_datetime(d['time']),
        'temperature': [
            round((hi + lo) / 2, 1)
            for hi, lo in zip(d['temperature_2m_max'], d['temperature_2m_min'])
        ],
        'precipitation': d['precipitation_sum'],
        'conditions':    [_wmo_to_condition(c) for c in d['weathercode']],
    })
    return df


def predict_next_week(model: RandomForestRegressor, location,
                       bun_cost: float = 0.35,
                       cache_dir: str = 'data/weather_cache') -> pd.DataFrame:
    """
    Predict bun orders for the next 7 days using the weather forecast.

    Returns a DataFrame with one row per day:
      day, day_name, predicted_buns, temperature, conditions, cost_estimate
    """
    forecast = fetch_weather_forecast(location.latitude, location.longitude, cache_dir)
    forecast = prepare_features(forecast)

    forecast['predicted_buns'] = model.predict(forecast[FEATURES]).round().astype(int)
    forecast['day_name']       = forecast['day'].dt.strftime('%A')
    forecast['date_label']     = forecast['day'].dt.strftime('%d %b')
    forecast['cost_estimate']  = (forecast['predicted_buns'] * bun_cost).round(2)

    return forecast[[
        'day', 'day_name', 'date_label',
        'predicted_buns', 'cost_estimate',
        'temperature', 'precipitation', 'conditions',
    ]]
