import os
import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from streamlit_autorefresh import st_autorefresh

# ── DB connection string ─────────────────────────────────
DATABASE_URL = "postgresql://postgres:password@localhost:5432/dash3"

if not DATABASE_URL:
    st.error(
        "❌ DATABASE_URL is not set.\n\n"
        "• Locally → `export DATABASE_URL=postgresql://user:pass@host:5432/db`\n"
        "• Streamlit Cloud → add it in **Secrets**."
    )
    st.stop()

try:
    engine = create_engine(DATABASE_URL)
    # quick ping
    with engine.connect() as conn:
        conn.execute("SELECT 1")
except OperationalError as e:
    st.error("🚫 Could not connect to PostgreSQL:\n\n" + str(e.orig))
    st.stop()

# ── Streamlit page config ────────────────────────────────
st.set_page_config(page_title="NBA Finals Dashboard", layout="wide")
st.title("🏀 NBA Finals – Live Dashboard")

# Manual refresh button
if st.button("🔁 Manual Refresh"):
    st.rerun()

# Auto-refresh every 60 000 ms (60 s)
st_autorefresh(interval=60_000, key="autoRefresh")

# ── Load data (with try/except) ──────────────────────────
def load_query(sql: str):
    try:
        return pd.read_sql(sql, engine)
    except Exception as err:
        st.error(f"DB error while running:\n{sql}\n\n{err}")
        return pd.DataFrame()

player_df = load_query(
    """
    SELECT * FROM player_stats
    WHERE pts IS NOT NULL
    ORDER BY time_collected DESC
    LIMIT 100
    """
)

team_df = load_query(
    """
    SELECT * FROM team_stats
    ORDER BY time_collected DESC
    LIMIT 2
    """
)

pbp_df = load_query(
    """
    SELECT * FROM play_by_play
    ORDER BY time_collected DESC, eventnum DESC
    LIMIT 30
    """
)

# ── Visuals ───────────────────────────────────────────────
c1, c2 = st.columns(2)

with c1:
    st.subheader("Top Scorers")
    if player_df.empty:
        st.info("No player rows yet.")
    else:
        fig = px.bar(
            player_df.sort_values("pts", ascending=False).head(10),
            x="player_name", y="pts", title="Top Scoring Players"
        )
        st.plotly_chart(fig, use_container_width=True)

with c2:
    st.subheader("Team Points Breakdown")
    if team_df.empty:
        st.info("No team rows yet.")
    else:
        fig = px.pie(
            team_df, names="team_name", values="pts", title="Team Score Share"
        )
        st.plotly_chart(fig, use_container_width=True)

st.subheader("Live Player Stats (last 100 rows)")
st.dataframe(player_df)

st.subheader("Latest Play-by-Play Events")
st.dataframe(pbp_df)
