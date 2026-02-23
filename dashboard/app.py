"""
Hood Burger — Analytics Dashboard

Run from the burger_analytics/ root folder:
    streamlit run dashboard/app.py
"""

import sys, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
from datetime import date
from sqlalchemy import create_engine

# ── page config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="Hood Burger — Analytics", page_icon="🍔", layout="wide")

DB_PATH = os.path.join(ROOT, 'data', 'demo_pos_data.db')

# ── colour palettes ───────────────────────────────────────────────────────────
DARK = dict(
    bg='#0B0F17', surface='#111827', border='#243041',
    text='#E5E7EB', muted='#9CA3AF', muted2='#6B7280',
    accent='#CF2708', good='#16A34A', warn='#D97706', bad='#DC2626',
    series1='#64748B', series2='#94A3B8', blue='#3B82F6',
    bar='#E07040', bar2='#374151',
)
LIGHT = dict(
    bg='#F7F8FA', surface='#FFFFFF', border='#E5E7EB',
    text='#111827', muted='#6B7280', muted2='#9CA3AF',
    accent='#CF2708', good='#16A34A', warn='#D97706', bad='#DC2626',
    series1='#64748B', series2='#94A3B8', blue='#2563EB',
    bar='#E07040', bar2='#94A3B8',
)

GRID_DARK  = 'rgba(156,163,175,0.12)'
GRID_LIGHT = 'rgba(100,116,139,0.15)'

# Shared heatmap colorscale — cool grey → teal → amber → orange (no white, no black)
HEAT_SCALE = [
    [0.00, '#69767C'],
    [0.15, '#758E93'],
    [0.30, '#85A1A0'],
    [0.50, '#C88D6B'],
    [0.70, '#ED7630'],
    [0.82, '#FC7021'],
    [0.92, '#FE620A'],
    [1.00, '#FE5004'],
]


# ── CSS injection ─────────────────────────────────────────────────────────────
def inject_css(T, dark: bool):
    if dark:
        override = f"""
        .stApp, [data-testid="stAppViewContainer"] {{ background-color: {T['bg']} !important; }}
        [data-testid="stHeader"] {{ background-color: {T['bg']} !important; }}
        section[data-testid="stSidebar"] {{
            background-color: {T['surface']} !important;
            border-right: 1px solid {T['border']} !important;
        }}
        .stMarkdown p, .stCaption {{ color: {T['muted']} !important; }}
        h1, h2, h3 {{ color: {T['text']} !important; }}
        hr {{ border-color: {T['border']} !important; opacity: 1 !important; }}
        .stCheckbox label, .stCheckbox label p,
        .stToggle label, .stToggle label p,
        .stRadio label, .stRadio label p,
        .stSelectbox label, .stSelectbox label p,
        [data-testid="stWidgetLabel"] p,
        [data-testid="stWidgetLabel"] span {{ color: {T['text']} !important; }}
        """
    else:
        override = f"""
        section[data-testid="stSidebar"] {{ border-right: 1px solid {T['border']}; }}
        hr {{ border-color: {T['border']} !important; opacity: 1 !important; }}
        .stCaption, [data-testid="stCaptionContainer"] {{ color: {T['muted']} !important; }}
        """

    st.markdown(f"""<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; }}

div[data-testid="stMetric"] {{
    background: {T['surface']} !important;
    border: 1px solid {T['border']} !important;
    border-radius: 12px;
    padding: 16px 20px;
}}
div[data-testid="stMetric"] label {{
    color: {T['muted']} !important;
    font-size: 11px !important;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: .05em;
}}
[data-testid="stMetricValue"] > div {{
    color: {T['text']} !important;
    font-size: 26px !important;
    font-weight: 700 !important;
}}
[data-testid="stMetricDelta"] {{ color: {T['muted']} !important; font-size: 12px !important; }}
h1 {{ font-size: 22px !important; font-weight: 700; margin-bottom: 2px; }}
h2 {{ font-size: 16px !important; font-weight: 600; margin: 24px 0 4px 0; }}
h3 {{ font-size: 14px !important; font-weight: 600; margin: 12px 0 2px 0; }}
{override}
</style>""", unsafe_allow_html=True)


# ── plotly helpers ────────────────────────────────────────────────────────────
def bi(fig, T, GRID, height=350):
    axis = dict(
        gridcolor=GRID, zerolinecolor=GRID,
        tickfont=dict(color=T['muted'], size=11),
        title_font=dict(color=T['muted'], size=12),
    )
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=T['text'], family='Inter, sans-serif', size=12),
        xaxis=axis, yaxis=axis,
        legend=dict(font=dict(color=T['muted'], size=11),
                    bgcolor='rgba(0,0,0,0)', bordercolor='rgba(0,0,0,0)'),
        margin=dict(t=10, b=10, l=10, r=10),
        height=height,
    )
    return fig


def bi_heatmap(fig, T, height=420):
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=T['text'], family='Inter, sans-serif', size=11),
        xaxis=dict(side='top', tickfont=dict(color=T['muted'], size=11),
                   gridcolor='rgba(0,0,0,0)', zerolinecolor='rgba(0,0,0,0)'),
        yaxis=dict(tickfont=dict(color=T['muted'], size=11),
                   gridcolor='rgba(0,0,0,0)', zerolinecolor='rgba(0,0,0,0)'),
        margin=dict(t=10, b=10, l=10, r=10),
        height=height,
    )
    return fig


def apply_heatmap_scale(fig, z_values, T):
    """Apply HEAT_SCALE with full data range (nanmin → nanmax, no clipping)."""
    fig.update_traces(
        colorscale=HEAT_SCALE,
        zmin=float(np.nanmin(z_values)),
        zmax=float(np.nanmax(z_values)),
        colorbar=dict(
            tickfont=dict(color=T['muted'], size=10),
            title_font=dict(color=T['muted'], size=10),
            outlinewidth=0,
        ),
    )
    return fig


# ── data guard — auto-seed on first run (e.g. Streamlit Cloud) ───────────────
if not os.path.exists(DB_PATH):
    from datetime import date as _date
    from src.data_generator import seed_database as _seed
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with st.spinner("Generating demo data — first run takes 2–3 minutes…"):
        _seed(
            db_path=DB_PATH,
            start_date=_date(2022, 1, 1),
            end_date=_date(2025, 12, 31),
        )
    st.rerun()


# ── load data ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_all_data(db_path: str):
    engine = create_engine(f'sqlite:///{db_path}')
    df_txn = pd.read_sql("""
        SELECT id, total_amount,
               CAST(strftime('%H', timestamp) AS INTEGER) AS hour,
               strftime('%Y-%m', timestamp)               AS month,
               DATE(timestamp)                            AS day
        FROM transactions
    """, engine)
    df_txn['day'] = pd.to_datetime(df_txn['day'])

    df_weather = pd.read_sql("""
        SELECT DATE(timestamp) AS day, temperature, precipitation, conditions
        FROM weather_snapshots
    """, engine)
    df_weather['day'] = pd.to_datetime(df_weather['day'])

    df_buns = pd.read_sql("""
        SELECT date, ordered_buns, actual_buns_used, waste_percentage
        FROM daily_bun_records ORDER BY date
    """, engine)
    df_buns['date'] = pd.to_datetime(df_buns['date'])

    df_buns_weather = pd.read_sql("""
        SELECT b.date AS day, b.actual_buns_used,
               w.temperature, w.precipitation, w.conditions
        FROM daily_bun_records b
        LEFT JOIN weather_snapshots w ON DATE(w.timestamp) = b.date
        ORDER BY b.date
    """, engine)
    df_buns_weather['day'] = pd.to_datetime(df_buns_weather['day'])

    return df_txn, df_weather, df_buns, df_buns_weather


df_txn, df_weather, df_buns, df_buns_weather = load_all_data(DB_PATH)


# ── sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    logo_path = os.path.join(ROOT, 'docs', 'logo.webp')
    if os.path.exists(logo_path):
        st.image(logo_path, use_container_width=True)
    else:
        st.title("Hood Burger")
    st.caption("Kongresni trg 3, Ljubljana")
    st.divider()

    st.subheader("Filter by date")
    date_range = st.date_input(
        "Select range",
        value=(date(2022, 1, 1), date(2025, 12, 31)),
        min_value=date(2022, 1, 1),
        max_value=date(2025, 12, 31),
    )
    if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
        start, end = date_range
    else:
        start, end = date(2022, 1, 1), date(2025, 12, 31)
    start_ts = pd.Timestamp(start)
    end_ts   = pd.Timestamp(end)

    st.divider()
    dark_mode = st.toggle("Dark mode", value=True)
    st.divider()
    st.caption("Weather: Open-Meteo (real data)")
    st.caption("Sales: synthetic demo data")


# ── theme — must come after sidebar reads dark_mode ──────────────────────────
T    = DARK if dark_mode else LIGHT
GRID = GRID_DARK if dark_mode else GRID_LIGHT
inject_css(T, dark_mode)


# ── apply date filter ─────────────────────────────────────────────────────────
txn     = df_txn[(df_txn['day']   >= start_ts) & (df_txn['day']   <= end_ts)]
buns    = df_buns[(df_buns['date'] >= start_ts) & (df_buns['date'] <= end_ts)]
weather = df_weather[(df_weather['day'] >= start_ts) & (df_weather['day'] <= end_ts)]

daily = txn.groupby('day').agg(
    transactions=('id', 'count'),
    revenue=('total_amount', 'sum'),
).reset_index()
daily_weather = daily.merge(weather, on='day', how='left')
n_days = max(daily['day'].nunique(), 1)

# Previous period for KPI deltas
period_len = max((end_ts - start_ts).days, 1)
prev_end   = start_ts - pd.Timedelta(days=1)
prev_start = prev_end  - pd.Timedelta(days=period_len)
txn_prev   = df_txn[(df_txn['day']   >= prev_start) & (df_txn['day']   <= prev_end)]
buns_prev  = df_buns[(df_buns['date'] >= prev_start) & (df_buns['date'] <= prev_end)]


# ── header + KPIs ─────────────────────────────────────────────────────────────
st.title("Hood Burger — Analytics")
st.caption(f"{start.strftime('%d %b %Y')} — {end.strftime('%d %b %Y')}  ·  {n_days} days")

st.header("Performance Overview")

total_revenue  = txn['total_amount'].sum()
avg_daily_txn  = len(txn) / n_days
avg_waste_pct  = buns['waste_percentage'].mean() if len(buns) > 0 else 0
waste_eur      = int((buns['ordered_buns'] - buns['actual_buns_used']).sum()) * 0.35

prev_revenue   = txn_prev['total_amount'].sum()
prev_avg_txn   = len(txn_prev) / period_len

def pct_delta(curr, prev):
    if prev == 0: return None
    return f"{(curr - prev) / prev:+.1%}"

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Revenue",          f"€{total_revenue:,.0f}",  pct_delta(total_revenue, prev_revenue))
col2.metric("Avg Transactions / Day", f"{avg_daily_txn:.0f}",    pct_delta(avg_daily_txn, prev_avg_txn))
col3.metric("Avg Bun Waste",          f"{avg_waste_pct:.1f}%")
col4.metric("Buns Wasted (€ cost)",   f"€{waste_eur:,.0f}")

st.divider()


# ── bar charts ────────────────────────────────────────────────────────────────
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Sales by Hour of Day")

    hourly = (
        txn.groupby('hour')['id']
        .count().div(n_days).round(1)
        .reset_index(name='avg_transactions')
    )
    peak_hours = hourly.nlargest(2, 'avg_transactions')['hour'].tolist()
    hourly['color'] = hourly['hour'].apply(
        lambda h: T['accent'] if h in peak_hours else T['series1']
    )
    fig1 = go.Figure(go.Bar(
        x=hourly['hour'], y=hourly['avg_transactions'],
        marker_color=hourly['color'],
        text=hourly['avg_transactions'],
        texttemplate='%{text:.1f}', textposition='outside',
        hovertemplate='%{x}:00 — %{y:.1f} avg transactions<extra></extra>',
    ))
    fig1.update_layout(xaxis=dict(tickmode='linear', dtick=1))
    bi(fig1, T, GRID)
    st.plotly_chart(fig1, use_container_width=True)

with col_right:
    st.subheader("Revenue by Month")

    monthly = txn.groupby('month').agg(revenue=('total_amount', 'sum')).reset_index()
    fig2 = px.bar(
        monthly, x='month', y='revenue',
        labels={'month': 'Month', 'revenue': 'Revenue (EUR)'},
        color='revenue',
        color_continuous_scale=[[0, T['bar2']], [0.5, T['bar']], [1, T['accent']]],
        text='revenue',
    )
    fig2.update_traces(texttemplate='€%{text:,.0f}', textposition='outside')
    fig2.update_layout(
        coloraxis_showscale=False,
        xaxis_tickangle=-45,
        uniformtext_minsize=7, uniformtext_mode='hide',
    )
    bi(fig2, T, GRID)
    st.plotly_chart(fig2, use_container_width=True)


# ── scatter + bun waste ───────────────────────────────────────────────────────
col_left2, col_right2 = st.columns(2)

with col_left2:
    st.subheader("Sales vs Temperature")

    df_s = daily_weather.dropna(subset=['temperature', 'conditions']).copy()
    df_s['weather_group'] = df_s['conditions'].apply(
        lambda c: 'Clear / Sunny' if c == 'Clear' else 'Rain / Clouds / Other'
    )
    fig3 = go.Figure()
    color_map = {'Clear / Sunny': T['accent'], 'Rain / Clouds / Other': T['blue']}
    for group, color in color_map.items():
        sub = df_s[df_s['weather_group'] == group]
        fig3.add_trace(go.Scatter(
            x=sub['temperature'], y=sub['transactions'],
            mode='markers', name=group,
            marker=dict(color=color, size=5, opacity=0.55),
            hovertemplate='%{x:.1f}°C — %{y} transactions<extra>' + group + '</extra>',
        ))
    if len(df_s) > 1:
        m, b_coef = np.polyfit(df_s['temperature'], df_s['transactions'], 1)
        x_rng = np.array([df_s['temperature'].min(), df_s['temperature'].max()])
        fig3.add_trace(go.Scatter(
            x=x_rng.tolist(), y=(m * x_rng + b_coef).tolist(),
            mode='lines', name='Trend',
            line=dict(color=T['muted2'], width=2, dash='dash'),
        ))
        fig3.add_annotation(
            x=x_rng[-1], y=(m * x_rng + b_coef)[-1],
            text=f"+{m:.1f} txn/°C", showarrow=False,
            xanchor='left', font=dict(size=11, color=T['muted']),
        )
    fig3.update_layout(
        xaxis_title='Daily avg temperature (°C)',
        yaxis_title='Transactions',
        legend=dict(orientation='h', yanchor='bottom', y=1.01, x=0),
    )
    bi(fig3, T, GRID)
    st.plotly_chart(fig3, use_container_width=True)

with col_right2:
    st.subheader("Daily Bun Waste — The Problem")

    buns_plot = buns.copy()
    buns_plot['waste_30d'] = buns_plot['waste_percentage'].rolling(30, min_periods=1).mean()
    fig4 = go.Figure()
    fig4.add_trace(go.Scatter(
        x=buns_plot['date'], y=buns_plot['waste_percentage'],
        mode='markers', name='Daily',
        marker=dict(color=T['bar'], size=3, opacity=0.4),
    ))
    fig4.add_trace(go.Scatter(
        x=buns_plot['date'], y=buns_plot['waste_30d'],
        mode='lines', name='30-day avg',
        line=dict(color=T['accent'], width=2),
    ))
    fig4.add_hrect(
        y0=8, y1=12, fillcolor=T['accent'], opacity=0.07,
        annotation_text='Over-order range (8–12%)',
        annotation_position='top left',
    )
    fig4.update_layout(
        xaxis_title='Date', yaxis_title='Waste %',
        yaxis=dict(range=[0, 18]),
        legend=dict(orientation='h', yanchor='bottom', y=1.01, x=0),
    )
    bi(fig4, T, GRID)
    st.plotly_chart(fig4, use_container_width=True)


# ── pattern analysis ──────────────────────────────────────────────────────────
st.divider()
st.header("Pattern Analysis")
st.caption(
    "Each cell is one specific combination. Hover for the exact value. "
    "Bright yellow = highest activity, dark purple = lowest."
)

txn_heat = txn.copy()
txn_heat['dow_num']   = txn_heat['day'].dt.dayofweek
txn_heat['month_str'] = txn_heat['day'].dt.strftime('%Y-%m')

DOW_ORDER   = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
DOW_NUMS    = [0, 1, 2, 3, 4, 5, 6]
HOUR_LABELS = [f"{h:02d}:00" for h in range(9, 23)]
n_weeks     = max(n_days / 7, 1)

# Metric toggle above both columns so they stay vertically aligned
h2_metric = st.radio(
    "Month × Day of Week — show:",
    ["Avg Transactions", "Avg Revenue (€)"],
    horizontal=True, key='h2_metric',
)

col_h1, col_h2 = st.columns(2)

# ── heatmap 1: Hour × Day of Week ────────────────────────────────────────────
with col_h1:
    st.subheader("Hour × Day of Week")
    st.caption("When is demand highest on each day of the week?")

    pivot1 = (
        txn_heat.groupby(['hour', 'dow_num'])['id']
        .count().div(n_weeks).round(1)
        .reset_index(name='avg_txn')
        .pivot(index='hour', columns='dow_num', values='avg_txn')
        .reindex(index=range(9, 23), columns=DOW_NUMS).fillna(0)
    )
    n_h = len(HOUR_LABELS)
    cd1 = np.stack([
        np.array([[HOUR_LABELS[i]] * 7 for i in range(n_h)]),
        np.array([DOW_ORDER for _ in range(n_h)]),
    ], axis=-1)

    fig_h1 = go.Figure(go.Heatmap(
        z=pivot1.values, x=DOW_ORDER, y=HOUR_LABELS,
        text=pivot1.values.round(1),
        texttemplate='%{text:.0f}',
        textfont=dict(color='white', size=10),
        customdata=cd1,
        hovertemplate='%{customdata[0]} on %{customdata[1]}: <b>%{z:.1f}</b> avg transactions<extra></extra>',
        showscale=True, colorbar=dict(title='Avg txn'),
    ))
    fig_h1.update_layout(yaxis_autorange='reversed')
    apply_heatmap_scale(fig_h1, pivot1.values, T)
    bi_heatmap(fig_h1, T)
    st.plotly_chart(fig_h1, use_container_width=True)


# ── heatmap 2: Month × Day of Week ───────────────────────────────────────────
with col_h2:
    st.subheader("Month × Day of Week")

    available_years = sorted(txn_heat['day'].dt.year.unique().tolist())
    use_year = st.checkbox("Filter by single year", key='h2_year_filter')
    if use_year:
        sel_year   = st.selectbox("Year", available_years,
                                  index=len(available_years) - 1, key='h2_year')
        heat2_data = txn_heat[txn_heat['day'].dt.year == sel_year].copy()
        heat2_data['month_key'] = heat2_data['day'].dt.strftime('%b')
        MONTH_ORDER = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                       'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        caption_txt = f"Seasonality by weekday — {sel_year}"
    else:
        heat2_data  = txn_heat.copy()
        heat2_data['month_key'] = heat2_data['day'].dt.strftime('%Y-%m')
        MONTH_ORDER = None
        caption_txt = "Seasonality by weekday — full selected range"

    st.caption(caption_txt)

    day_counts = (
        heat2_data[['day', 'month_key', 'dow_num']]
        .drop_duplicates(subset='day')
        .groupby(['month_key', 'dow_num'])['day']
        .count().reset_index(name='n_occ')
    )

    if h2_metric == "Avg Transactions":
        agg = heat2_data.groupby(['month_key', 'dow_num'])['id'].count().reset_index(name='total')
        agg = agg.merge(day_counts, on=['month_key', 'dow_num'], how='left')
        agg['value'] = (agg['total'] / agg['n_occ']).round(1)
        cb_title, hover_unit = 'Avg txn', 'avg transactions'
    else:
        agg = heat2_data.groupby(['month_key', 'dow_num'])['total_amount'].sum().reset_index(name='total')
        agg = agg.merge(day_counts, on=['month_key', 'dow_num'], how='left')
        agg['value'] = (agg['total'] / agg['n_occ']).round(0)
        cb_title, hover_unit = 'Avg €/day', 'avg revenue'

    pivot2 = (
        agg.pivot(index='month_key', columns='dow_num', values='value')
        .reindex(columns=DOW_NUMS).fillna(0)
    )
    if MONTH_ORDER:
        pivot2 = pivot2.reindex([m for m in MONTH_ORDER if m in pivot2.index])
    month_labels = pivot2.index.tolist()
    n_m = len(month_labels)
    cd2 = np.stack([
        np.array([[m] * 7 for m in month_labels]),
        np.array([DOW_ORDER for _ in range(n_m)]),
    ], axis=-1)

    fig_h2 = go.Figure(go.Heatmap(
        z=pivot2.values, x=DOW_ORDER, y=month_labels,
        text=pivot2.values.round(1),
        texttemplate='%{text:.0f}',
        textfont=dict(color='white', size=10),
        customdata=cd2,
        hovertemplate=f'%{{customdata[0]}} — %{{customdata[1]}}: <b>%{{z:.1f}}</b> {hover_unit}<extra></extra>',
        showscale=True, colorbar=dict(title=cb_title),
    ))
    apply_heatmap_scale(fig_h2, pivot2.values, T)
    bi_heatmap(fig_h2, T)
    st.plotly_chart(fig_h2, use_container_width=True)


# ── heatmap 3: Temperature × Day of Week ─────────────────────────────────────
st.subheader("Temperature × Day of Week")
st.caption("Does the terrace effect hit all days equally, or only weekends?")

df_tw = daily_weather.dropna(subset=['temperature']).copy()
df_tw['dow_num'] = df_tw['day'].dt.dayofweek
df_tw['temp_bin'] = pd.cut(
    df_tw['temperature'],
    bins=[-15, 0, 5, 10, 15, 20, 25, 35],
    labels=['< 0°C', '0–5°C', '5–10°C', '10–15°C', '15–20°C', '20–25°C', '> 25°C'],
)
pivot3 = (
    df_tw.groupby(['temp_bin', 'dow_num'])['transactions']
    .mean().round(1).reset_index()
    .pivot(index='temp_bin', columns='dow_num', values='transactions')
    .reindex(columns=DOW_NUMS).fillna(0)
)
temp_labels = pivot3.index.astype(str).tolist()
n_t = len(temp_labels)
cd3 = np.stack([
    np.array([[t] * 7 for t in temp_labels]),
    np.array([DOW_ORDER for _ in range(n_t)]),
], axis=-1)

fig_h3 = go.Figure(go.Heatmap(
    z=pivot3.values, x=DOW_ORDER, y=temp_labels,
    text=pivot3.values.round(1),
    texttemplate='%{text:.0f}',
    textfont=dict(color='white', size=10),
    customdata=cd3,
    hovertemplate='%{customdata[0]} on %{customdata[1]}: <b>%{z:.1f}</b> avg transactions<extra></extra>',
    showscale=True, colorbar=dict(title='Avg txn'),
))
apply_heatmap_scale(fig_h3, pivot3.values, T)
bi_heatmap(fig_h3, T, height=320)
st.plotly_chart(fig_h3, use_container_width=True)


# ── heatmap 4: Hour × Month ───────────────────────────────────────────────────
st.subheader("Hour × Month")
st.caption(
    "Does the lunch or dinner peak shift across the year? "
    "Reveals which months need more staff at specific hours."
)

MONTH_NAMES = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
               'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
txn_heat['month_num'] = txn_heat['day'].dt.month

month_day_counts = (
    txn_heat[['day', 'month_num']].drop_duplicates()
    .groupby('month_num')['day'].count()
    .rename('n_days_m')
)
agg4 = txn_heat.groupby(['hour', 'month_num'])['id'].count().reset_index(name='total')
agg4 = agg4.join(month_day_counts, on='month_num')
agg4['avg_txn'] = (agg4['total'] / agg4['n_days_m']).round(1)

pivot4 = (
    agg4.pivot(index='hour', columns='month_num', values='avg_txn')
    .reindex(index=range(9, 23), columns=range(1, 13)).fillna(0)
)
month_col_labels = [MONTH_NAMES[m - 1] for m in pivot4.columns]
n_h4 = len(HOUR_LABELS)
cd4  = np.stack([
    np.array([[HOUR_LABELS[i]] * 12 for i in range(n_h4)]),
    np.array([month_col_labels for _ in range(n_h4)]),
], axis=-1)

fig_h4 = go.Figure(go.Heatmap(
    z=pivot4.values, x=month_col_labels, y=HOUR_LABELS,
    text=pivot4.values.round(1),
    texttemplate='%{text:.0f}',
    textfont=dict(color='white', size=10),
    customdata=cd4,
    hovertemplate='%{customdata[0]} in %{customdata[1]}: <b>%{z:.1f}</b> avg transactions<extra></extra>',
    showscale=True, colorbar=dict(title='Avg txn'),
))
fig_h4.update_layout(yaxis_autorange='reversed')
apply_heatmap_scale(fig_h4, pivot4.values, T)
bi_heatmap(fig_h4, T, height=420)
st.plotly_chart(fig_h4, use_container_width=True)


# ── prediction & action ───────────────────────────────────────────────────────
from src.predictor import (
    prepare_features, train_model, evaluate_model,
    get_feature_importance, predict_next_week,
)

st.divider()
st.header("Prediction & Action")
st.caption(
    "Model trained on 3 years of history → tested on the final 12 months it has never seen. "
    "Use the 7-day order table to place tomorrow's bun order."
)


@st.cache_data
def build_model(df_bw: pd.DataFrame):
    df_feat = prepare_features(df_bw)
    cutoff  = df_feat['day'].max() - pd.DateOffset(months=12)
    train   = df_feat[df_feat['day'] <= cutoff].copy()
    test    = df_feat[df_feat['day'] >  cutoff].copy()
    model   = train_model(train)
    metrics = evaluate_model(model, test)
    fi      = get_feature_importance(model)
    return model, metrics, fi, cutoff


model, metrics, fi, cutoff = build_model(df_buns_weather)

BUN_COST          = 0.35
avg_buns_day      = df_buns_weather['actual_buns_used'].mean()
avg_waste_rate    = df_buns['waste_percentage'].mean() / 100
TARGET_ERROR_RATE = 0.05   # industry standard on real data (vs ~10% current waste)

annual_buns      = avg_buns_day * 365
annual_waste_now = annual_buns * avg_waste_rate * BUN_COST
annual_waste_mdl = annual_buns * TARGET_ERROR_RATE * BUN_COST
annual_saving    = max(0, annual_waste_now - annual_waste_mdl)

mc1, mc2, mc3, mc4 = st.columns(4)
mc1.metric("Model accuracy",          f"{100 - metrics['mape']:.1f}%",
           help="100% = perfect. Synthetic data inflates this — expect ~90% on real data.")
mc2.metric("Avg error",               f"±{metrics['mae']:.0f} buns/day")
mc3.metric("Annual waste cost (now)", f"€{annual_waste_now:,.0f}",
           help=f"Current {avg_waste_rate:.0%} over-ordering × €{BUN_COST}/bun × 365 days.")
mc4.metric("Projected annual saving", f"€{annual_saving:,.0f}",
           help=f"Assumes 5% model error on real data vs current {avg_waste_rate:.0%} waste.")

st.caption(
    f"Trained on: up to {cutoff.strftime('%d %b %Y')}.  "
    f"Tested on: {cutoff.strftime('%d %b %Y')} → end of data."
)

pred_left, pred_right = st.columns([1, 1])

with pred_left:
    st.subheader("What drives the prediction?")
    st.caption("Higher = more influence on the model's output.")

    fig_fi = go.Figure(go.Bar(
        x=fi['importance'],
        y=fi['feature'].map({
            'day_of_week':   'Day of week',
            'month':         'Month',
            'year':          'Year (growth)',
            'is_weekend':    'Weekend flag',
            'temperature':   'Temperature',
            'precipitation': 'Precipitation',
            'is_rain':       'Rain flag',
            'is_hot_sunny':  'Hot & sunny flag',
        }),
        orientation='h',
        marker_color=T['bar'],
        text=fi['importance'].map(lambda x: f'{x:.1%}'),
        textposition='outside',
        textfont=dict(color=T['muted']),
    ))
    fig_fi.update_layout(
        xaxis=dict(showticklabels=False),
        margin=dict(t=10, b=10, l=10, r=60),
    )
    bi(fig_fi, T, GRID, height=320)
    st.plotly_chart(fig_fi, use_container_width=True)

with pred_right:
    st.subheader("Order for next 7 days")
    st.caption("P50 = best estimate. P90 = safety buffer (order on busy or uncertain days).")

    engine_pred = create_engine(f'sqlite:///{DB_PATH}')
    location    = engine_pred.connect().execute(
        __import__('sqlalchemy').text("SELECT latitude, longitude FROM locations LIMIT 1")
    ).fetchone()

    try:
        from types import SimpleNamespace
        loc     = SimpleNamespace(latitude=location[0], longitude=location[1])
        week_df = predict_next_week(model, loc, bun_cost=BUN_COST)

        week_df['order_p90'] = (
            week_df['predicted_buns'] + 1.28 * metrics['mae']
        ).round().astype(int)

        display_df = week_df[['day_name', 'date_label', 'predicted_buns', 'order_p90',
                               'temperature', 'conditions', 'cost_estimate']].copy()
        display_df.columns = ['Day', 'Date', 'P50 (order)', 'P90 (safe)',
                               'Temp (°C)', 'Weather', 'Cost (€)']
        display_df['Temp (°C)'] = display_df['Temp (°C)'].map(lambda x: f'{x:.1f}°')
        display_df['Cost (€)']  = display_df['Cost (€)'].map(lambda x: f'€{x:.2f}')

        st.dataframe(display_df, hide_index=True, use_container_width=True)
        st.caption(
            f"Total this week (P50): **{week_df['predicted_buns'].sum():,} buns**  ·  "
            f"P90: {week_df['order_p90'].sum():,} buns"
        )

    except Exception as e:
        st.warning(f"Could not fetch live forecast: {e}")
        st.caption("Weather forecast requires an internet connection.")


# ── model vs reality ──────────────────────────────────────────────────────────
st.subheader("Model vs Reality — Test Period")
st.caption(
    "Orange = actual buns used. Blue = model prediction. "
    "Red dots = large misses (>2× avg error) — worth investigating: holiday? event? bad weather?"
)

df_res = metrics['df_results'].copy()
df_res['day'] = pd.to_datetime(df_res['day'])
df_an  = df_res[np.abs(df_res['error']) > metrics['mae'] * 2]

fig_pred = go.Figure()
fig_pred.add_trace(go.Scatter(
    x=df_res['day'], y=df_res['actual'],
    mode='lines', name='Actual buns used',
    line=dict(color=T['bar'], width=1.5),
))
fig_pred.add_trace(go.Scatter(
    x=df_res['day'], y=df_res['predicted'],
    mode='lines', name='Model prediction',
    line=dict(color=T['blue'], width=1.5, dash='dot'),
))
if len(df_an) > 0:
    fig_pred.add_trace(go.Scatter(
        x=df_an['day'], y=df_an['actual'],
        mode='markers', name='Large miss — investigate',
        marker=dict(color=T['accent'], size=8, symbol='circle'),
        hovertemplate=(
            '%{x|%d %b %Y}<br>Actual: %{y}<br>'
            'Error: %{customdata:+.0f} buns<extra>Investigate</extra>'
        ),
        customdata=df_an['error'].values,
    ))

fig_pred.update_layout(
    xaxis_title='Date', yaxis_title='Buns',
    legend=dict(orientation='h', yanchor='bottom', y=1.01, x=0),
)
bi(fig_pred, T, GRID, height=320)
st.plotly_chart(fig_pred, use_container_width=True)


# ── footer ────────────────────────────────────────────────────────────────────
st.divider()
st.caption(
    f"Bun cost: €{BUN_COST}/bun (client estimate: 60–100 buns/day wasted ≈ €10k/year).  "
    f"  |  Data range: 2022-01-01 to 2025-12-31  |  Growth: +6%/year"
)
