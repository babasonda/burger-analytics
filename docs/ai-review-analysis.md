# AI Review Analysis — Burger Analytics
*Compiled: 2026-02-24*
*Purpose: Evaluate external AI feedback against our current implementation and define development priorities.*

---

## Context

This document analyses feedback from an external AI tool on how to build a restaurant demand forecasting system.
The goal is to identify what we already have, what is genuinely missing, and what is noise or premature.

---

## 1. What We Already Got Right

Before listing gaps, it is worth noting that several things the external AI highlighted we already implemented correctly:

| Their Recommendation | Our Status |
|---|---|
| Temporal train/test split (never random) | ✅ Done — train first 3 years, test last year |
| Weather as a feature (rain flag, temp flag) | ✅ Done — `is_rain`, `is_hot_sunny` |
| Calendar/seasonality features | ✅ Done — `day_of_week`, `month`, `is_weekend` |
| Year trend feature | ✅ Done — `year` feature captures +6% annual growth |
| Point forecast dashboard | ✅ Done — 7-day table in Streamlit |
| MAE as primary accuracy metric | ✅ Done — `evaluate_model()` returns MAE |
| Free weather API, no key needed | ✅ Done — Open-Meteo, cached locally |

The foundation is solid. We did not make the common beginner mistakes (random splits, no weather, no trend).

---

## 2. Gaps — Ordered by Priority

### Priority 1: Missing Metrics (High Impact, Low Effort)

**What we have:** MAE and MAPE only.

**What is missing:**

- **WAPE (Weighted Absolute Percentage Error)** — better than MAPE because it does not explode on low-volume days. For a restaurant with variable daily demand, WAPE gives a more honest picture than MAPE.
  - Formula: `sum(|actual - predicted|) / sum(actual)`
  - Add to `evaluate_model()` in `predictor.py`

- **Bias (Mean Error)** — tells us if we systematically over- or under-predict.
  - Formula: `mean(predicted - actual)` — positive = we over-order, negative = we under-order
  - Critical for bun waste analysis. If our model has negative bias, it will make the waste problem worse, not better.
  - Add to `evaluate_model()` in `predictor.py`

- **Service Level** — what % of days did we predict enough buns (predicted >= actual)?
  - Most operationally meaningful metric for the client
  - Add to `evaluate_model()` in `predictor.py`

**Why now:** These are 10-line additions to existing code. They make the demo much stronger.

---

### Priority 2: Quantile Forecasting (High Business Value, Medium Effort)

**What we have:** Point forecast only — one number per day.

**What is missing:** P50/P80/P90 forecasts.

The external AI explained this well. For our client:
- P50 = median prediction (minimize waste, accept some stockout risk)
- P80 = order enough to cover demand on 80% of days (balance)
- P90 = very safe, higher waste (good for busy event days)

**Why this matters for buns specifically:**
A stockout (running out of buns) is visible to customers and means lost sales. The client likely wants P75–P80 as default, not P50.

**How to implement:**
`RandomForestRegressor` does not natively produce quantiles.
Options:
1. **Simple approach:** Apply a percentage buffer to the P50 forecast (e.g., P80 = P50 × 1.10). Quick, explainable to the client.
2. **Proper approach:** Switch to `GradientBoostingRegressor` with `loss='quantile'` or use `sklearn`'s `QuantileRegressor`. More correct but more complex.

**Recommendation:** Start with the simple buffer approach for the demo. Label it clearly. Upgrade to proper quantile regression later.

---

### Priority 3: Lag Features (Medium Impact, Low Effort)

**What we have:** Only static calendar and weather features.

**What is missing:** Yesterday's sales, last week's same day, rolling 7-day average.

Lag features are powerful because:
- If Monday was unusually busy, Tuesday is often still elevated
- Last week's Wednesday is the best single predictor of this Wednesday
- Rolling averages smooth out anomalies

**How to add:**
In `prepare_features()`, add:
```python
df = df.sort_values('day')
df['lag_1']        = df['actual_buns_used'].shift(1)   # yesterday
df['lag_7']        = df['actual_buns_used'].shift(7)   # same day last week
df['rolling_7']    = df['actual_buns_used'].shift(1).rolling(7).mean()
```

**Caveat:** Lag features require the historical series to be present. For live 7-day forecasting, you need the last 7 days of actual data. This is feasible since the DB stores `daily_bun_records`.

**Recommendation:** Add lag features in next development session. High ROI.

---

### Priority 4: Event Calendar in the Model (High Business Value, Already Planned)

**What we have:** `SPECIAL_EVENTS` hardcoded dict in `data_generator.py`. Not used as a model feature.

**What is missing:** `is_event` and `event_multiplier` as model features. These explain the biggest demand spikes (New Year ×1.8, Marathon ×1.5).

**Why critical:** Without event features, the model will be surprised by every marathon or festival. The client will notice this immediately when a big event causes a stockout.

**Already planned in architecture:** The `calendar_events` table is agreed but not yet built. This is the right next schema addition.

**Recommendation:** Add `calendar_events` table + `is_event` binary feature to model. This is the highest-value single feature missing from the model.

---

### Priority 5: Backtesting (Medium Effort, Strong for Client Demo)

**What we have:** One train/test split.

**What is missing:** Simulating historical decisions — "if we had used this model in 2023, what would our waste and stockout record have looked like?"

Backtesting is more convincing than accuracy metrics for a client. Instead of "MAE = 18 buns," you say:
*"If you had used this model in 2023, your annual bun waste cost would have been €4,200 instead of €9,800."*

That is a business story, not a statistics report.

**Recommendation:** Build this after the core model is stable. It requires running `predict_next_week()` iteratively over historical dates.

---

## 3. What Is Premature (Ignore for Now)

The external AI covered advanced topics that are real but not relevant yet:

| Topic | Why to Skip for Now |
|---|---|
| Gradient Boosting (XGBoost/LightGBM) | Random Forest is already performing well. Upgrade only if RF hits a ceiling. |
| SHAP explanations | Useful for feature importance, but feature importance chart we already have covers the demo. |
| Hierarchical forecasting | We have 1 location. Relevant when we expand. |
| Bayesian / probabilistic forecasting | Advanced. Skip until after quantile regression is working. |
| Causal inference (promo uplift) | Relevant when promotions table is built and live. |
| Formal optimization solvers | Far future. Our simple order table is enough for now. |

---

## 4. Pricing and Business Context

The external AI confirmed our positioning is reasonable. Key points for the client conversation:

- **MVP pilot range:** €3k–€15k for a small chain. We are building a strong pilot.
- **Ongoing managed service:** €300–€2,000/location/month. Post-pilot upsell.
- **SaaS tools (MarketMan, Orca):** ~$199/month/location. We compete on customisation and local insight, not price alone.

**How to frame the demo:**
Do not say "AI forecasting platform." Say:
> *"We reduce your bun waste by 60–80% by predicting demand for the next 7 days using weather, day of week, and events. Pilot: 6 weeks, 1 location, top 3 prep items."*

That is easier to sell than a technical system description.

---

## 5. Recommended Development Sequence

Based on business value vs implementation effort:

### Phase 1 — Strengthen Current Model (Next 1–2 sessions)
1. Add WAPE + Bias + Service Level to `evaluate_model()`
2. Add P80 buffer to 7-day forecast table (simple: ×1.10)
3. Add lag features (`lag_7` first — highest single-feature gain)

### Phase 2 — Event Integration (Next 2–3 sessions)
4. Build `calendar_events` table in `db_models.py`
5. Add `is_event` feature to `prepare_features()`
6. Populate calendar with 2022–2025 Ljubljana events

### Phase 3 — Backtesting and Client Story (Before first client demo)
7. Build backtest function: simulate model decisions over 2023
8. Calculate "waste saved" and "stockouts avoided" in euros
9. Add backtest results to dashboard as a dedicated section

### Phase 4 — Quantile Regression (After Phase 3)
10. Implement proper P50/P75/P90 with quantile-aware model
11. Add order recommendation slider to dashboard (client adjusts risk tolerance)

---

## 6. Key Concepts to Understand (Learning Priorities)

For Nace specifically — learn these in order:

1. **Bias** — understand why a model can have good MAE but still be wrong in a predictable direction
2. **WAPE vs MAPE** — understand why percentage errors break on small numbers
3. **Service Level** — this is the metric the kitchen manager actually cares about
4. **P50/P80 tradeoff** — waste vs stockout, not just "accuracy"
5. **Lag features** — why yesterday's sales predict tomorrow better than the weather alone
6. **Backtesting** — why one train/test split is not enough to convince a client

These six concepts will make the whole project "click" at a business level.

---

## Summary

The external AI review confirms we are on the right track architecturally. The biggest gaps are:
1. Richer evaluation metrics (WAPE, Bias, Service Level)
2. Quantile forecasting (P50/P80/P90 for operational decisions)
3. Lag features (strongest missing predictor)
4. Event calendar integrated into the model (biggest demand driver not yet modelled)

None of these require rebuilding. They are incremental additions to what we already have.

---

*End of document.*
