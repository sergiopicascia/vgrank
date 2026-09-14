"""
VideoGame Ranking - Streamlit entry point.

This file only declares the pages of the app; the content of each page lives
in the ``pages/`` folder.

Run with:  streamlit run app.py
"""

import streamlit as st

st.set_page_config(page_title="VideoGame Ranking", page_icon="🎮", layout="wide")

pages = [
    st.Page("pages/ranking.py", title="Ranking", icon="🏆", default=True),
    st.Page("pages/add_game.py", title="Add game", icon="➕"),
    st.Page("pages/insights.py", title="Insights", icon="📊"),
]

st.navigation(pages).run()
