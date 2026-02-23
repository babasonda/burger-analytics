# Session State — Burger Analytics Dashboard

Last updated: 2026-02-22

---

## Session 3 (2026-02-22)

### What we did
- Switched weather source from OpenWeatherMap → **Open-Meteo** (free, no API key, no registration)
- Rewrote `src/weather.py`:
  - `fetch_openmeteo()` — one HTTP call fetches all 2 years of hourly data
  - `parse_daily_summaries()` — aggregates hourly → daily: avg temp, total precip, dominant condition
  - `fetch_and_store_weather()` — main entry point, synthetic fallback if API unreachable
  - `_store_synthetic()` — Ljubljana climate fallback, never needs internet
- Updated `src/data_generator.py` `seed_database()`:
  - Removed `use_real_weather` and `openweathermap_api_key` params
  - Always uses Open-Meteo (automatic fallback to synthetic if offline)
- Updated `notebooks/exploration.ipynb`:
  - No API key setup required
  - 4 charts: sales by hour, by month, vs temperature, bun waste %
  - Trendline uses numpy (no statsmodels dependency)

### Everything in `notebooks/exploration.ipynb` is complete and ready to run.

---

## How to run

```bash
# From burger_analytics/ root
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
jupyter notebook
# Open notebooks/exploration.ipynb → Run All
# First run: ~2-3 minutes
# Weather is cached after first fetch — never re-downloaded
```

---

## What exists (all files complete)
- ✅ `src/db_models.py` — 6 tables including DailyBunRecord
- ✅ `src/data_generator.py` — 2-year POS data, events, bun waste
- ✅ `src/weather.py` — Open-Meteo, cached, synthetic fallback
- ✅ `notebooks/exploration.ipynb` — 4-chart client demo
- ✅ `requirements.txt` — all dependencies listed

---

## Session 6 additions (2026-02-22)
- Updated bun cost to €0.35 (client estimate: 60–100 buns/day wasted = ~€10k/year)
- Extended synthetic data to 4 full years: 2022–2025 with +6%/year growth
- Added bad day simulation (~1x/year, -40 to -70% transactions)
- Added SPECIAL_EVENTS for 2022 and 2025
- Built `src/predictor.py` — Random Forest regression model:
  - Features: day_of_week, month, year, is_weekend, temperature, precipitation, is_rain, is_hot_sunny
  - Train: first 3 years | Test: last 12 months (temporal split)
  - Outputs: accuracy %, avg error buns/day, projected savings
  - 7-day forecast using Open-Meteo forecast API
- Added Prediction section to dashboard: feature importance, next 7 days table, predicted vs actual chart
- Added scikit-learn to requirements.txt
- **User needs to:** delete data/demo_pos_data.db + weather cache, run notebook to regenerate

## Session 5 additions (2026-02-22)
- Answered architectural questions: security, multi-location, real data value, promotions schema
- Updated CLAUDE.md: added Opus/Sonnet guidance, security principles, planned schema additions
- Updated learning-journal.md: skill evolution, analytics levels, heatmap theory, ML concepts
- Added 3 heatmaps to dashboard/app.py:
  1. Hour × Day of week (the "poker matrix" — busiest slot by day and time)
  2. Month × Day of week (seasonality broken down by weekday)
  3. Temperature bucket × Day of week (does weather hit all days equally?)
- All heatmaps update when date range filter changes

## Session 4 additions (2026-02-22)
- Built `dashboard/app.py` — Streamlit interactive dashboard
- Added `streamlit` to requirements.txt
- Run with: `streamlit run dashboard/app.py`

## Next agreed steps (after running the dashboard)
1. Run notebook, verify all 4 charts look correct
2. Decide on next feature — candidates:
   - Predictive bun ordering model (regression: day_of_week + weather forecast)
   - Event calendar integration for upcoming spikes
   - Week-ahead forecast chart added to notebook

---

## Open questions
- What is the actual bun cost per unit? (affects the € waste estimate in Chart 4)
- Do we want to add more locations, or go deeper on analytics for one location first?

---

End of session-state document.
