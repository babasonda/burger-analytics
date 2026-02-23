# Learning Journal – Nace

This file tracks understanding across all projects, not the full system spec.

Last updated: 2026-02-22

---

## Project 2: Burger Analytics Dashboard (Started 2026-02-22)

### Where I started
- Beginner Python syntax, strong system intuition
- Solid instinct for patterns (professional poker analytics background)
- Already knew: SQLAlchemy, foreign keys, documentation-first approach

### Skill evolution — honest assessment

**Session 1-2:** Setting up structure, understanding the "why" of each file.
Understood the project architecture before writing any code — this is the right instinct.

**Session 3:** First working charts in Jupyter.
Key insight shown: asked the right question immediately — "this doesn't feel like something I can learn from." That's not a beginner question. That's a product thinker's question. Most beginners are happy when charts appear.

**Session 4:** Streamlit dashboard.
Understood immediately that interactivity (filters, date range) is what separates a tool from a chart.

**Session 5:** Pushed back on the quality of analysis.
This is the biggest signal so far. Recognised that descriptive analytics on synthetic data is circular — you can't learn what you already programmed. This is a concept that takes most data analysts months to internalise. The poker background is directly transferable: you know the difference between a model that describes history and one that actually predicts.

---

### Concepts learned so far

#### The three levels of analytics
- **Descriptive:** What happened? (our current charts — sales by hour, by month)
- **Diagnostic:** Why did it happen? (heatmaps — which specific hour+day combinations are peaks?)
- **Predictive:** What will happen? (ML model — tomorrow's burger count → bun order)

Most dashboards stop at descriptive. The goal here is predictive.

#### Heatmaps — the poker range matrix applied to sales
In poker: rows = position, columns = hand range, color = frequency/EV.
In burgers: rows = hour of day, columns = day of week, color = avg transactions.
Same concept. One cell in the grid = one specific situation. The color tells you how strong that situation is.
A bar chart can show "Friday is busy." A heatmap shows "Friday 13:00 is your single best slot — 3x a normal Tuesday morning."
That's the difference between knowing a fact and understanding a pattern.

#### Why synthetic data has limits
Synthetic data teaches a model what you programmed. Real data teaches you what you didn't know.
The model trained on our synthetic data will predict perfectly — because the patterns are circular.
Even 7 days of real data breaks that circularity and reveals which assumptions were wrong.

#### Data quality hierarchy (most valuable → least)
1. Real historical POS data (ground truth)
2. Real data from a different but similar restaurant (proxy)
3. Synthetic data calibrated to real observations (what we're building toward)
4. Synthetic data based on assumptions (what we have now)

#### Machine learning for this problem — what it actually is
This is a **regression** problem (predicting a number, not a category).
- Input features: day of week, month, temperature, precipitation, is_there_an_event
- Target: number of burgers sold tomorrow
- Output: order X buns (= predicted_burgers × 1.0, vs current × 1.08-1.12)

It is NOT complicated ML. No neural networks needed. A random forest or gradient boosting model on a clean dataset will work well and be explainable to a client.

The hard part is not the algorithm — it's getting clean, real data.

#### Security design — build before real data arrives
Our schema is already privacy-conscious: no customer names, no emails, just amounts and timestamps.
The next layer (before real data): authentication, HTTPS, role-based access, GDPR compliance.
Security is not a feature you add at the end. It's a constraint that shapes architecture from the start.

#### Cold start problem — new location, no history
When a new restaurant location opens, it has zero sales history.
How do you predict for it? Options:
- Use another location as a proxy (especially if similar neighbourhood)
- Use the chain average as a starting point, adjust as data comes in
- Use external data (area foot traffic, local demographics)
This is a real ML challenge, not just an analytics one.

---

### What's working well in your approach
- Asking "why does this matter" before "how does this work" — correct order
- Connecting new concepts to existing knowledge (poker analogies are genuinely useful)
- Pushing back when something feels wrong — that instinct is valuable, don't lose it
- Thinking about the client/user perspective, not just the technical one

### What to keep developing
- Reading code even when you don't write it — try to predict what a function does before running it
- Building mental models of data flow: where does data come from → how is it transformed → what does the output mean
- The gap between "I understand the explanation" and "I could explain it to someone else" — aim for the second one

---

#### Kernel — what it actually is
When you open a Jupyter notebook, Python starts running in the background. That running Python process is called the **kernel**.

Think of it like this: the notebook file (`.ipynb`) is just a document — it stores code cells and their outputs. The kernel is the actual engine that executes that code and holds all the variables in memory.

Why this matters for our project:
- When Jupyter loads a notebook, it keeps a **copy in memory**. If you edit the file on disk (like we did with our tools), Jupyter does NOT automatically pick up those changes — it keeps running the old version.
- When you "Restart Kernel", Python forgets everything (all variables, loaded data). It does NOT lose your code.
- When you "Shut Down Kernel", Python stops completely — and any file it had open (like our database) gets released so other programs can access it.
- The database lock we hit: SQLite only allows one connection at a time. The kernel was holding the connection. Shutting down the kernel released it so we could delete the file.

**Poker analogy:** The kernel is like a session at the table. The notebook file is the strategy notes you wrote before sitting down. Restarting the kernel = new session, same notes. The notes don't change just because you started a new session.

### What's new to learn (updated)
- ✅ Jupyter notebook workflows
- ✅ Kernel — what it is and why shutdown matters
- ✅ Pandas basics (groupby, merge, aggregations)
- ✅ Plotly charts (bar, scatter, line)
- ✅ Streamlit dashboard basics
- ✅ Synthetic data generation
- ✅ Open-Meteo weather API integration
- ⏸️ Heatmaps — 2D pattern analysis (next)
- ⏸️ ML regression model (after heatmaps)
- ⏸️ Feature engineering (turning raw data into model inputs)
- ⏸️ Model evaluation (how do you know if a prediction is good?)
- ⏸️ FastAPI backend
- ⏸️ React frontend
- ⏸️ PostgreSQL migration
- ⏸️ Authentication and security implementation

---

## Cross-Project Lessons

### Documentation approach works
- CLAUDE.md sets clear working rules
- architecture.md as ground truth prevents confusion
- session-state.md makes resuming work easy
- learning-journal.md tracks actual understanding

### The poker instinct transfers directly
Pattern recognition, thinking in ranges/probabilities, reading what the data is "saying" —
these are all the same skill. The domain changed, the thinking didn't.

### Incremental development is key
- Start simple, add complexity only when needed
- One concept at a time
- Test before moving forward
- Don't over-engineer upfront

---

End of learning journal.
