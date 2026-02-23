# Burger Analytics Dashboard

Data analytics and visualization system for a burger restaurant chain in Ljubljana, Slovenia (4 locations).

## Project Status

**Current phase:** Jupyter exploration with lorem ipsum POS data + real weather data

**Long-term goal:** Full web dashboard with real-time POS integration, predictive analytics, inventory insights

---

## Quick Start

### 1. Setup

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Install dependencies (once requirements.txt is created)
pip install -r requirements.txt
```

### 2. Launch Jupyter

```bash
jupyter notebook
```

Open `notebooks/exploration.ipynb` and start exploring.

---

## Project Structure

```
burger_analytics/
├── docs/              # Documentation (architecture, learning journal, session state)
├── notebooks/         # Jupyter notebooks for exploration and analysis
├── data/              # SQLite database + weather cache
└── src/               # Reusable Python modules (models, generators, API integrations)
```

---

## Documentation

All project state is tracked in `docs/`:

- **CLAUDE.md** — Project instructions for Claude Code (working style, constraints)
- **architecture.md** — Ground truth of what exists right now (stack, schema, files)
- **learning-journal.md** — Nace's learning progress and understanding
- **session-state.md** — Where we left off last time and what's next

Read these before making changes.

---

## Tech Stack

- **Python** — Core language
- **Jupyter** — Interactive analysis and exploration
- **SQLAlchemy** — Database ORM
- **pandas** — Data manipulation
- **plotly/matplotlib** — Visualizations
- **SQLite** — Database (local dev), will migrate to PostgreSQL for production
- **OpenWeatherMap API** — Real weather data

---

## License

MIT (or whatever you choose)
