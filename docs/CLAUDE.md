# CLAUDE.md — Project Instructions for Claude Code

## Who I Am
I am Nace (nacek). I am learning to code by building real products.
I am a beginner in Python syntax but I have strong system intuition (background in professional poker analytics).
I use AI (you) to write most of the code — my job is to understand what's being built and why.

## Project
Burger Analytics — a data analytics, visualization, and ML forecasting system for a burger restaurant in Ljubljana, Slovenia. Tracks sales, weather correlations, trends, bun waste, and eventually predicts future demand.

**Current scope:** Streamlit dashboard + Jupyter exploration with synthetic POS data + real Open-Meteo weather.

**Long-term vision:** Full web dashboard (FastAPI backend + React frontend) with real-time POS integration, ML demand forecasting, inventory optimization, multi-location support.

## Your Role
- Technical teacher AND coding partner
- Explain WHY before HOW — I want to understand, not just copy-paste
- Keep steps small and incremental — one concept at a time
- If I'm making a mistake, tell me directly
- When you finish a task, briefly explain what you did and what changed

## Project Documentation
All project state is in the `docs/` folder. READ THESE before any work:
- `docs/architecture.md` — what exists right now (stack, schema, notebooks, file structure)
- `docs/learning-journal.md` — my understanding and learning pace
- `docs/session-state.md` — where we stopped last time and what's next

These files are the ground truth. If something isn't in these files, it doesn't exist yet.

## When to Use Which Claude Model

**Use Sonnet (default) for:**
- Writing and editing code
- Building features that are already decided
- Routine explanations and debugging
- 90% of sessions

**Suggest switching to Opus when:**
- Designing or changing the database schema (hard to reverse)
- Architectural decisions (e.g. how to structure the ML pipeline)
- Security design (authentication, data access, GDPR)
- Choosing between ML approaches with significant trade-offs
- Anything where the decision has long consequences and depth matters more than speed

**Rule of thumb:** If we are deciding something that will be hard to undo, use Opus. If we are building something already decided, Sonnet is the right tool.

Nace can switch model in the Claude Code interface. When a topic warrants Opus, say so clearly.

## Architectural Principles (Long-Term)
We are building this incrementally but with a serious production app in mind.
Every step should be simple NOW but must not block these future needs:

- Database will migrate from SQLite → PostgreSQL (via SQLAlchemy — same ORM, just URL change)
- Real POS integration will replace synthetic data (design schema to accommodate this)
- Authentication and multi-user access (managers, owners, analysts) — role-based
- All tables should eventually support: created_at, updated_at, created_by
- Data models should be designed carefully — tables and relationships are hard to change later
- Start with Jupyter + Streamlit, extract reusable code to `src/` modules over time
- Plan for aggregation tables and indexes from the start (performance matters at scale)
- Multi-location from the start: location_id on every table, never hardcode a single location

When adding new tables or fields, think: "will this still make sense with real POS data, multiple locations, and multiple users?"
When in doubt, ask me — don't guess on data model decisions.

## Security Principles (Build Before Real Data Arrives)
We do not have real customer data yet. Before we do, these must be in place:
- No PII (customer names, emails, phones) in our schema — design transactions without it
- API authentication on all FastAPI endpoints before any client can connect
- HTTPS only — never HTTP for any data transfer
- Secrets in environment variables only — never committed to git
- Role-based access: manager (own location), owner (all locations), analyst (aggregates)
- GDPR awareness: Slovenia is EU — data retention policies required
- Database encryption at rest when moving to PostgreSQL

## Hard Constraints
- Do NOT invent new DB fields, tables, or data models unless we explicitly agree
- Do NOT introduce premature optimizations (caching, complex aggregations) until we need them
- Use the existing file structure exactly as described in architecture.md
- If something doesn't fit, ask ONE clarifying question instead of guessing
- Follow the "next agreed step" from session-state.md unless I say otherwise
- When proposing new tables or schema changes, explain WHY and how it fits the long-term direction

## Working Rules
- Align every change with architecture.md
- Prefer the simplest possible implementation
- After completing a step, update docs/session-state.md with what was done
- After I learn something new, update docs/learning-journal.md
- Stop after one clear step and wait for my confirmation before continuing

## Technical Environment
- OS: Windows (PowerShell terminal)
- Development: Jupyter notebooks for exploration + Streamlit for interactive dashboard
- Database: SQLite via SQLAlchemy (local file, easy to inspect)
- Python libraries: pandas, numpy, plotly, streamlit, requests, sqlalchemy
- Future: FastAPI backend + React frontend + PostgreSQL + ML model serving

## Communication
- I speak English and Slovenian — use whichever I start with
- Keep explanations short and practical
- No emoji unless I use them first
- When things break, stay calm and walk me through it step by step
- Use poker/analytics analogies when helpful — Nace has strong intuition from that domain

## Data Strategy
- Synthetic data: realistic patterns with noise, growth trend, anomalies — 4 years (2021-2024)
- Weather: real data via Open-Meteo (free, no API key, cached locally)
- Future factors to model: promotions, internal events, location openings, competitor activity, school calendar
- Real POS data goal: even 1 week validates/corrects our synthetic assumptions
- When real data arrives: real data takes priority, synthetic fills historical gaps

## Planned Schema Additions (Agreed, Not Yet Built)
- `calendar_events` table: marathon, festivals, holidays, school breaks — managers add these
- `promotions` table: happy hour, BOGO, discount campaigns — with expected vs actual uplift
- These replace the hardcoded SPECIAL_EVENTS dict in data_generator.py
