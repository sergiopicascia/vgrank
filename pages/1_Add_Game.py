"""
Page "Add game": search a game on RAWG, give it a score in every category and
add it to the collection.
"""

import streamlit as st

from vgrank.api import ApiError, search_games
from vgrank.collection import GameCollection
from vgrank.models import Game
from vgrank.scoring import CATEGORIES, MAX_SCORE, MIN_SCORE, WEIGHTS, overall_score

st.set_page_config(page_title="Add game - VideoGame Ranking", page_icon="🎮", layout="wide")

st.title("➕ Add and rate a game")


# --- Step 1: search ---------------------------------------------------------

st.subheader("1. Search the game")


@st.cache_data(show_spinner="Searching on RAWG...")
def cached_search(query):
    """Call the API once per query: identical searches reuse the previous result."""
    return search_games(query)


query = st.text_input("Game title", placeholder="e.g. Hollow Knight")

if query.strip() == "":
    st.info("Type a title above to start.")
    st.stop()

try:
    results = cached_search(query.strip())
except ApiError as error:
    st.error(str(error))
    st.stop()

if len(results) == 0:
    st.warning("No game found, try a different title.")
    st.stop()

# Show titles with the release year so that remakes and sequels can be told apart.
labels = []
for game in results:
    year = game["released"][:4] if game["released"] else "unknown year"
    labels.append(f"{game['title']} ({year})")

chosen_label = st.selectbox("Pick the right game", labels)
chosen = results[labels.index(chosen_label)]

col_image, col_info = st.columns([1, 2])
with col_image:
    if chosen["image_url"] != "":
        st.image(chosen["image_url"], width="stretch")
with col_info:
    st.markdown(f"### {chosen['title']}")
    st.write("**Released:**", chosen["released"] or "unknown")
    st.write("**Genres:**", ", ".join(chosen["genres"]) or "unknown")
    st.write("**Platforms:**", ", ".join(chosen["platforms"]) or "unknown")
    st.write("**Metacritic:**", chosen["metacritic"] if chosen["metacritic"] is not None else "n/a")


# --- Step 2: rate -----------------------------------------------------------

st.subheader("2. Rate it")

scores = {}
columns = st.columns(len(CATEGORIES))
for column, category in zip(columns, CATEGORIES):
    with column:
        scores[category] = st.slider(
            f"{category.capitalize()} (weight {WEIGHTS[category]:.0%})",
            MIN_SCORE,
            MAX_SCORE,
            value=7,
        )

st.metric("Overall score", f"{overall_score(scores):.2f}")


# --- Step 3: save -----------------------------------------------------------

st.subheader("3. Add to the ranking")

if st.button("Add to my ranking", type="primary"):
    new_game = Game(
        game_id=chosen["game_id"],
        title=chosen["title"],
        released=chosen["released"],
        genres=chosen["genres"],
        platforms=chosen["platforms"],
        metacritic=chosen["metacritic"],
        image_url=chosen["image_url"],
        scores=scores,
    )

    collection = GameCollection().load()
    try:
        collection.add(new_game)
        st.success(f"'{new_game.title}' added with an overall score of {new_game.overall():.2f}!")
    except ValueError as error:
        st.warning(str(error))
