import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px
import time

# === DATABASE CONNECTION ===
engine = create_engine('postgresql://postgres:password@localhost:5432/dash3')

# === PAGE SETUP ===
st.set_page_config(page_title="NBA Finals Dashboard", layout="wide")
st.title("🏀 NBA Finals 2025 – Live Game 1 Dashboard")

# === MANUAL REFRESH BUTTON ===
if st.button("🔁 Manual Refresh"):
    st.rerun()

# === PLAYER STATS ===
try:
    player_df = pd.read_sql("""
        SELECT * FROM player_stats
        WHERE pts IS NOT NULL
        ORDER BY time_collected DESC
        LIMIT 100
    """, engine)
except Exception as e:
    st.error(f"Could not load player stats: {e}")
    player_df = pd.DataFrame()

# === TEAM STATS ===
try:
    team_df = pd.read_sql("""
        SELECT * FROM team_stats
        ORDER BY time_collected DESC
        LIMIT 2
    """, engine)
except Exception as e:
    st.error(f"Could not load team stats: {e}")
    team_df = pd.DataFrame()

# === PLAY-BY-PLAY EVENTS ===
try:
    pbp_df = pd.read_sql("""
        SELECT * FROM play_by_play
        ORDER BY time_collected DESC, event_num DESC
        LIMIT 20
    """, engine)
except Exception as e:
    st.error(f"Could not load play-by-play data: {e}")
    pbp_df = pd.DataFrame()

# === CHARTS SECTION ===
col1, col2 = st.columns(2)

with col1:
    st.subheader("Top Scorers")
    if not player_df.empty:
        fig = px.bar(player_df.sort_values(by="pts", ascending=False).head(10),
                     x="player_name", y="pts", title="Top Scoring Players")
        st.plotly_chart(fig)
    else:
        st.info("No player data available yet.")

with col2:
    st.subheader("Team Points Breakdown")
    if not team_df.empty:
        fig2 = px.pie(team_df, names="team_name", values="points", title="Team Score Share")
        st.plotly_chart(fig2)
    else:
        st.info("No team data available yet.")

# === STATS TABLE ===
st.subheader("Live Player Stats")
if not player_df.empty:
    st.dataframe(player_df[['player_name', 'team_id', 'min', 'pts', 'reb', 'ast', 'fg_pct', 'usg_pct']])
else:
    st.info("Waiting for player stats...")

# === PLAY-BY-PLAY TABLE ===
st.subheader("Latest Play-by-Play Events")
if not pbp_df.empty:
    st.dataframe(pbp_df[['period', 'clock', 'home_desc', 'visitor_desc']])
else:
    st.info("Waiting for play-by-play data...")

# === AUTO REFRESH EVERY 60 SECONDS (put this at the end) ===
time.sleep(60)
st.experimental_rerun()
