import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px
import time
# === CONFIG ===
DATABASE_URL = 'postgresql://postgres:password@localhost:5432/dash'
engine = create_engine(DATABASE_URL)

# === STREAMLIT SETUP ===
st.set_page_config(page_title="NBA Finals Dashboard", layout="wide")
st.title("🏀 NBA Finals 2025 – Live Game 1 Dashboard")

# === AUTO-REFRESH EVERY 60 SECONDS ===
st_autorefresh = st.experimental_rerun if st.button("🔁 Manual Refresh") else None
time.sleep(60)

# === PLAYER STATS ===
player_df = pd.read_sql("""
    SELECT * FROM player_stats
    WHERE pts IS NOT NULL
    ORDER BY time_collected DESC
    LIMIT 100
""", engine)

# === TEAM STATS ===
team_df = pd.read_sql("""
    SELECT * FROM team_stats
    ORDER BY time_collected DESC
    LIMIT 2
""", engine)

# === PLAY-BY-PLAY ===
pbp_df = pd.read_sql("""
    SELECT * FROM play_by_play
    ORDER BY time_collected DESC, event_num DESC
    LIMIT 20
""", engine)

# === CHARTS ===
col1, col2 = st.columns(2)

with col1:
    st.subheader("Top Scorers")
    fig = px.bar(player_df.sort_values(by="pts", ascending=False).head(10),
                 x="player_name", y="pts", title="Top Scoring Players")
    st.plotly_chart(fig)

with col2:
    st.subheader("Team Points Breakdown")
    fig2 = px.pie(team_df, names="team_name", values="points", title="Team Score Share")
    st.plotly_chart(fig2)

# === STATS TABLE ===
st.subheader("Live Player Stats")
st.dataframe(player_df[['player_name', 'team_id', 'min', 'pts', 'reb', 'ast', 'fg_pct', 'usg_pct']])

# === PLAY-BY-PLAY ===
st.subheader("Latest Play-by-Play Events")
st.dataframe(pbp_df[['period', 'clock', 'home_desc', 'visitor_desc']])
