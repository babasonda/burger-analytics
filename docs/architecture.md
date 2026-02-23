# Burger Analytics Dashboard — Architecture (Current State)

Last updated: 2026-02-22

This file reflects the current, real state of the project – not plans.

---

## Project Overview

**Purpose:** Data analytics and visualization dashboard for a burger restaurant chain in Ljubljana, Slovenia (4 locations). Tracks sales trends, weather correlations, menu performance, and operational insights.

**Status:** Just started — Initial setup complete, ready for exploration in Jupyter

**Restaurant:** Burger Joint (fictional demo)
**Locations:** 4 Ljubljana locations
**Current data:** Lorem ipsum POS data + real weather API integration

---

## Stack

### Development Environment
- **Jupyter notebook** — exploratory analysis, visualizations
- Local: `http://localhost:8888`
- Entry point: `notebooks/exploration.ipynb`

### Database
- SQLite (development only)
- DB file: `data/demo_pos_data.db`
- ORM: SQLAlchemy
- Models file: `src/db_models.py`
- Will migrate to PostgreSQL when moving to production

### Python Libraries
- **pandas** — data manipulation, aggregations
- **plotly** or **matplotlib** — interactive charts
- **sqlalchemy** — database ORM
- **requests** — weather API calls

### Weather Data
- **OpenWeatherMap API** (free tier: 1000 calls/day)
- Cache API responses in `data/weather_cache/`
- Store historical snapshots in database

### Future (not built yet)
- FastAPI backend (REST API for web dashboard)
- React frontend (interactive dashboard UI)
- PostgreSQL database (production)

---

## Database Schema (Planned)

### 1. locations
**Purpose:** 1 Ljubljana burger joint location (Kongresni trg, with terrace)

Fields:
- id (PK)
- name (e.g., "Ljubljana Center", "BTC")
- address
- latitude, longitude (for weather API)
- opened_date
- has_terrace (for weather/sales correlation)
- is_active
- created_at, updated_at

### 2. transactions
**Purpose:** Individual customer orders (lorem ipsum + future real POS data)

Fields:
- id (PK)
- location_id (FK → locations)
- timestamp
- total_amount
- payment_method (cash / card / online)
- weather_snapshot_id (FK → weather_snapshots, nullable)
- created_at

### 3. order_items
**Purpose:** Line items for each transaction

Fields:
- id (PK)
- transaction_id (FK → transactions)
- item_id (FK → menu_items)
- quantity
- unit_price
- total_price

### 4. menu_items
**Purpose:** Burger menu (burgers, fries, drinks, sides)

Fields:
- id (PK)
- name (e.g., "Classic Burger", "Cheeseburger")
- category (burger / side / drink / dessert)
- base_price
- is_active
- created_at, updated_at

### 5. weather_snapshots
**Purpose:** Historical weather data for correlation analysis

Fields:
- id (PK)
- location_id (FK → locations)
- timestamp
- temperature (°C)
- precipitation (mm)
- conditions (e.g., "Clear", "Rain", "Snow")
- wind_speed
- humidity
- source ('synthetic' or 'openweathermap')
- created_at

### 6. daily_bun_records
**Purpose:** Per-day bun waste tracking — the core problem we're solving

Fields:
- id (PK)
- location_id (FK → locations)
- date
- ordered_buns (what was ordered from supplier)
- actual_buns_used (burgers sold that day = 1 bun each)
- waste_percentage ((ordered - used) / ordered × 100)
- created_at

---

## Data Generation Strategy

### Lorem Ipsum POS Data (Realistic)

**Locations:**
1. Ljubljana Center (Prešernov trg area)
2. BTC Shopping Center
3. Šiška neighborhood
4. Študentska (student area)

**Sales Patterns:**
- Lunch peak: 11:30–13:30
- Dinner peak: 18:00–20:00
- Weekdays vs weekends (students eat more on weekdays)
- Seasonality (summer = more drinks, winter = more soups)

**Menu Items (typical burger joint):**
- Burgers: Classic, Cheeseburger, Bacon Deluxe, Veggie, Chicken
- Sides: Fries, Onion Rings, Salad
- Drinks: Coke, Beer, Water, Coffee
- Desserts: Ice cream, Brownie

**Transaction Patterns:**
- Average order: 1.8 burgers, 1.5 sides, 1.2 drinks
- Average ticket: €12–18
- Payment mix: 60% card, 30% cash, 10% online

**Time Range:**
- 3 months of historical data
- ~500–800 transactions per location per week

### Real Weather Data

**OpenWeatherMap API:**
- Current weather: free, unlimited
- Historical weather (past 5 days): free, 1000 calls/day
- For demo: fetch current weather every hour, store in DB
- For correlation: match weather snapshot to each transaction timestamp

**Ljubljana coordinates:**
- Center: 46.0569° N, 14.5058° E
- BTC: 46.0721° N, 14.5494° E
- Šiška: 46.0708° N, 14.4883° E
- Študentska: 46.0490° N, 14.5058° E

---

## File Structure

```
burger_analytics/
├── docs/
│   ├── CLAUDE.md           ← Project instructions for Claude
│   ├── architecture.md     ← This file (ground truth of what exists)
│   ├── learning-journal.md ← Nace's learning progress
│   └── session-state.md    ← Where we left off, what's next
├── notebooks/
│   └── exploration.ipynb   ← Main Jupyter notebook (start here)
├── data/
│   ├── demo_pos_data.db    ← SQLite database
│   └── weather_cache/      ← Cached weather API responses
└── src/
    ├── db_models.py        ← SQLAlchemy models
    ├── data_generator.py   ← Lorem ipsum POS data generator
    └── weather.py          ← Weather API integration
```

---

## Current State

**What exists:**
- ✅ Project folder structure
- ✅ Documentation files (CLAUDE.md, architecture.md, learning-journal.md, session-state.md)
- ✅ .gitignore (Python/Jupyter)
- ✅ Database models (`src/db_models.py`) — 6 tables including DailyBunRecord
- ✅ Data generator (`src/data_generator.py`) — full 2-year transaction generation
- ✅ Weather module (`src/weather.py`) — synthetic Ljubljana weather + real OWM API
- ✅ Jupyter notebook (`notebooks/exploration.ipynb`) — 4-chart client demo
- ✅ `.env.example` — API key template

**Next steps:**
1. Run `pip install -r requirements.txt` in the virtual environment
2. Open `notebooks/exploration.ipynb` and run all cells (~2-3 min first run)
3. Register at openweathermap.org, add API key to `.env`, re-run with real weather
4. Review charts with the client and decide on next analytics features

---

## Development Workflow

### Starting a session
1. Read `docs/session-state.md` — where did we leave off?
2. Read `docs/architecture.md` — what exists right now?
3. Launch Jupyter: `jupyter notebook` from project root
4. Open `notebooks/exploration.ipynb`

### After completing work
1. Update `docs/architecture.md` with what was built
2. Update `docs/session-state.md` with current state and next steps
3. Suggest updates to `docs/learning-journal.md` if new concepts learned

---

## Future Roadmap (Not Building Yet)

### Phase 1: Jupyter Exploration (Current)
- Database models
- Lorem ipsum data generator
- Weather API integration
- Basic visualizations (sales by hour, weather correlation)

### Phase 2: Dashboard Prototype
- FastAPI backend (REST API)
- React frontend (charts, filters)
- PostgreSQL migration
- Real-time data refresh

### Phase 3: Advanced Analytics
- Predictive sales forecasting
- Inventory optimization
- Staff scheduling recommendations
- A/B testing for menu changes

### Phase 4: Production
- Real POS integration
- Multi-user authentication
- Mobile app
- Automated reports

---

End of architecture document.
