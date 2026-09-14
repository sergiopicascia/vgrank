"""
Page "Ranking": the table of rated games sorted by overall score.
"""

import streamlit as st

from vgrank import plots
from vgrank.collection import GameCollection
from vgrank.scoring import CATEGORIES, MAX_SCORE, MIN_SCORE


st.title("VideoGame Ranking")

collection = GameCollection().load()
ranking = collection.ranking()

if len(ranking) == 0:
    st.info("The ranking is empty. Open the **Add game** page to search a game and rate it.")
    st.stop()


# --- Sidebar: filters -------------------------------------------------------


def list_all_genres(table):
    """Return the sorted list of distinct genres found in the ``genres`` column."""
    genres = set()
    for text in table["genres"]:
        for genre in text.split(", "):
            if genre != "":
                genres.add(genre)
    return sorted(genres)


def has_any_genre(text, wanted_genres):
    """Return ``True`` if the comma separated ``text`` contains one of ``wanted_genres``."""
    for genre in text.split(", "):
        if genre in wanted_genres:
            return True
    return False


st.sidebar.header("Filters")
selected_genres = st.sidebar.multiselect("Genre", list_all_genres(ranking))
min_overall = st.sidebar.slider(
    "Minimum overall score", float(MIN_SCORE), float(MAX_SCORE), float(MIN_SCORE), step=0.5
)

filtered = ranking[ranking["overall"] >= min_overall]
if len(selected_genres) > 0:
    keep = filtered["genres"].apply(has_any_genre, wanted_genres=selected_genres)
    filtered = filtered[keep]

if len(filtered) == 0:
    st.warning("No game matches the current filters.")
    st.stop()


# --- Summary numbers --------------------------------------------------------

col_games, col_average, col_best = st.columns(3)
col_games.metric("Games rated", len(filtered))
col_average.metric("Average overall score", f"{filtered['overall'].mean():.2f}")
col_best.metric("Best game", filtered.iloc[0]["title"])


# --- Ranking table ----------------------------------------------------------

st.subheader("Ranking")

columns_to_show = ["rank", "image_url", "title", "released", "genres", "overall"] + CATEGORIES
column_labels = {
    "rank": "#",
    "image_url": st.column_config.ImageColumn("Cover"),
    "title": "Title",
    "released": "Released",
    "genres": "Genres",
    "overall": st.column_config.ProgressColumn(
        "Overall", min_value=0, max_value=MAX_SCORE, format="%.2f"
    ),
}
for category in CATEGORIES:
    column_labels[category] = category.capitalize()

st.dataframe(
    filtered[columns_to_show],
    column_config=column_labels,
    hide_index=True,
    width="stretch",
)


# --- Chart ------------------------------------------------------------------

st.subheader("Top games")
top_n = st.slider("How many games to show", 3, max(3, len(filtered)), min(10, len(filtered)))
st.pyplot(plots.ranking_bar_chart(filtered, top_n=top_n))


# --- Remove a game ----------------------------------------------------------

with st.expander("Remove a game from the ranking"):
    titles = list(ranking["title"])
    title_to_remove = st.selectbox("Game", titles)

    if st.button("Remove", type="primary"):
        game_id = int(ranking.loc[ranking["title"] == title_to_remove, "game_id"].iloc[0])
        collection.remove(game_id)
        st.success(f"'{title_to_remove}' removed.")
        st.rerun()  # reload the page so that the table is up to date
