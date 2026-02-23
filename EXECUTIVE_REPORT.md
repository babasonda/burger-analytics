# Hood Burger — Analytics Platform
## Executive Report & Pre-Implementation Questions

**Prepared by:** Burger Analytics Demo Project
**Date:** February 2026
**Status:** Proof of concept — synthetic data only

---

## What We Built

We built a fully working analytics and forecasting platform using **4 years of simulated sales data** (2022–2025), real Ljubljana weather from Open-Meteo, and a machine learning model that predicts daily burger demand.

The system has three layers:

| Layer | What it does |
|-------|-------------|
| **Analytics** | Shows when you sell most, how revenue changes by season, how weather affects sales |
| **Pattern analysis** | Heatmaps that reveal your busiest hour × day combinations at a glance |
| **Prediction** | Machine learning model that forecasts tomorrow's burger count so you order exactly that many buns |

Everything runs locally — no cloud, no subscription, no data sent anywhere.

---

## Key Findings from Synthetic Data

These numbers are from simulated data and should be validated against your real POS. They show what the model *can* reveal once real data is connected.

### Sales patterns
- **Peak hours:** 12:00–13:00 (lunch) and 18:00–19:00 (dinner) account for the majority of daily transactions
- **Weekend uplift:** Saturday and Sunday run approximately 30% higher than weekday average
- **Summer peak:** June–August shows highest revenue — the terrace effect is real and significant
- **Weather sensitivity:** Every +1°C above 15°C adds approximately 2–4 transactions per day on clear days. Rain reduces daily transactions by ~20%

### The bun waste problem
Our simulation models the current situation:
- The restaurant orders **8–12% more buns every day than it sells**
- That translates to roughly **33 buns wasted per day** in our model 
- At €0.35/bun, that is approximately **€4,200/year** in our model — scaled to your actual volume, likely **€7,500–12,000/year**

This waste is not random. It follows a predictable pattern tied to day of week, season, and weather. That is exactly what a model can learn.

### What the model achieves
Trained on 3 years of data, tested against 12 months it had never seen:
- The model predicts daily burger demand within **±20 buns on an average day**
- Industry-standard ML demand forecasting achieves **5% error** on real data vs the current blanket 10% over-order
- At 5% model error: **projected annual saving = ~€2,100** on buns alone

This number will change significantly — almost certainly upward — once real POS data replaces synthetic data. See the critical questions below.

---

## How the 7-Day Order Table Works

Every morning, the dashboard shows a table with two numbers for each day of the coming week:

### P50 (Base order)
The model's best estimate. There is a **50% chance actual demand lands below this number** and 50% above. This is the right number to order on a normal, average day.

### P90 (Safety buffer)
A higher number calculated as P50 + 1.28 × average model error. There is only a **10% chance demand exceeds this number**. Order P90 when:
- You cannot afford to run out (big event, weekend, sunny forecast)
- The supplier lead time is long and you cannot re-order quickly
- The weather forecast is unusually hot or you have a local event

**Simple rule:** Order P50 by default. Order P90 when you want to be safe.

The gap between P50 and P90 is the model's honest estimate of its own uncertainty. A smaller gap = more confident model. As real data is added, this gap will shrink.

---

## What This Tool Is Not (Honest Limitations)

Before connecting real data, it is important to be clear about what the current version cannot do:

1. **Circular data problem.** The model was trained on data we generated. It learned exactly what we programmed. On real data, it will face genuine surprises — a concert, a competitor closing, a heatwave — and its initial accuracy will be lower than what the dashboard shows.

2. **Single ingredient.** We modelled bun waste only. In a real restaurant, waste happens across all perishable ingredients. The platform is designed to expand to all SKUs but today it only tracks buns.

3. **Single location.** All data is for Kongresni trg 3. Multi-location support is designed into the database schema but not yet built into the dashboard.

4. **No real events calendar.** We hardcoded Ljubljana Marathon, Pustovanje, New Year, and summer festivals. Your real calendar will have dozens of events we do not know about — these will show up as anomalies (red dots on the backtesting chart) until they are added.

---

## Critical Questions — Before We Touch Real Data

These are the questions that will determine whether this project delivers real value or stays a demo.

### 1. Data availability
- What POS system do you use? (Toast, Square, Lightspeed, custom?)
- Can it export transaction-level data — ideally: timestamp, items ordered, quantities, prices?
- How far back does the export go? We need at least 12 months; 24+ months is significantly better
- Has the POS system changed in the last 3 years? If yes, when — and is the old data accessible?

### 2. The bun ordering process today
- Who decides how many buns to order each day — owner, manager, chef?
- What is the ordering process? (Call supplier, app, automatic?)
- What is your supplier's lead time — same day, next day, 48 hours?
- Are there minimum order quantities that make precision ordering harder?
- At what time of day does the order need to be placed?

### 3. Measuring waste right now
- Do you currently count unsold buns at end of day, or is 60–100 an estimate?
- Is waste tracked anywhere — even in a notebook or Excel?
- Are buns ever repurposed (bread baskets, staff meals) and would that count as waste?

### 4. Your real sales volume
- Roughly how many burgers do you sell on a typical weekday? Weekend day?
- Does a transaction typically include 1 burger, or often 2+ (table orders, families)?
- Do you have delivery (Wolt, Glovo) in addition to in-person? Are those in the same POS?

### 5. Seasonality and closures
- Is the terrace genuinely closed in winter, or just less used?
- Do you close on any holidays? (Christmas, Easter, Slovenian national holidays?)
- Have there been any unusual periods in the last 3 years — renovation, COVID restrictions, staff shortages — that created abnormal sales data?

### 6. Events and external factors
- What local events reliably bring more customers? (Markets, concerts, marathons?)
- Do you run internal promotions — happy hour, BOGO, seasonal menu — that spike demand?
- Are there regular catering or large group orders that skew daily bun counts?

### 7. Menu and pricing
- Have you changed bun prices or supplier in the last 2 years?
- Are all burgers one bun, or do any use brioche / double buns?
- Have you added or removed menu items that affect burger volume significantly?

### 8. Who uses this day-to-day
- Who would open the dashboard each morning to get the bun order?
- What device — phone, tablet, or desktop?
- Would you want it to send a WhatsApp or email with tomorrow's order automatically?

### 9. Definition of success
- What would make this worth your time in 6 months?
- Is the goal purely bun waste, or do you want to expand to all food costs?
- Are you planning to open additional locations in the next 12 months?

---

## What Happens When Real Data Arrives

**Week 1 with real data:**
- First genuine accuracy baseline — model error vs your actual demand
- Immediate identification of which events, weekdays, and weather conditions the model struggles with
- Real bun cost per unit confirmed → real waste cost calculated

**Month 1:**
- Model retrains on real history → accuracy improves significantly
- Red anomaly dots on the backtesting chart get investigated and explained
- Calendar events added (those you know in advance)

**Month 3:**
- Accuracy stabilises; the model has seen your real seasonal patterns
- P50/P90 gap narrows → you can order with more confidence
- Decision: expand to full ingredient tracking or keep buns only

**Month 6+:**
- Enough data to reliably detect year-on-year growth
- Possible expansion: multi-location comparison, promotion effectiveness tracking
- Possible next step: automatic daily order suggestion sent to your phone

---

## Technical Summary

| Component | Technology | Why |
|-----------|-----------|-----|
| Database | SQLite → PostgreSQL | Simple now, production-ready later |
| Data model | SQLAlchemy ORM | Same code works on both databases |
| Weather | Open-Meteo API | Free, real historical + 7-day forecast, no API key |
| Dashboard | Streamlit + Plotly | Interactive charts without building a web app |
| ML model | Random Forest (scikit-learn) | Handles non-linear patterns, gives feature importance, fast |
| Forecasting | Open-Meteo forecast API | Real Ljubljana weather for next 7 days |

All code is owned by you. No vendor lock-in. No ongoing subscription cost for the data sources.

---

## Recommended Next Step

**One conversation before any code work:**
Bring the answers to the questions above to a 1-hour working session. The goal of that session is not to import data — it is to decide:

1. Do we have enough historical data to train a meaningful model?
2. What does "waste" actually mean in your operation (counted how, by whom)?
3. What is the one metric that, if improved, would make this feel like a success?

The answers to those three questions will determine the entire shape of the real implementation.

---

*This report was generated from a proof-of-concept dashboard using 4 years of synthetic sales data for a fictitious location at Kongresni trg 3, Ljubljana. All numbers are illustrative. Real-world results will differ.*
