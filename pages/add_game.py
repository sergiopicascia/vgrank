"""
Page "Add game": search a game on RAWG, give it a score in every category and
add it to the collection.
"""

import streamlit as st

from vgrank.api import ApiError, search_games
from vgrank.collection import GameCollection
from vgrank.models import Game
from vgrank.scoring import CATEGORIES, MAX_SCORE, MIN_SCORE, WEIGHTS, overall_score

st.title("Add a game")


@st.cache_data(show_spinner="Searching on RAWG...")
def cached_search(query):
    """Call the API once per query: identical searches reuse the previous result."""
    return search_games(query)


# --- Search -----------------------------------------------------------------

query = st.text_input("Search a game", placeholder="e.g. Hollow Knight")

if query.strip() == "":
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

chosen_label = st.selectbox("Results", labels)
chosen = results[labels.index(chosen_label)]


# --- Game details and scores ------------------------------------------------

col_image, col_form = st.columns([1, 2], gap="large")

with col_image:
    if chosen["image_url"] != "":
        st.image(chosen["image_url"], width="stretch")
    st.subheader(chosen["title"])
    st.caption(
        f"{chosen['released'] or 'unknown date'} · {', '.join(chosen['genres']) or 'unknown genre'}"
    )
    st.caption(", ".join(chosen["platforms"]) or "unknown platforms")
    if chosen["metacritic"] is not None:
        st.caption(f"Metacritic: {chosen['metacritic']}")

with col_form:
    scores = {}
    for category in CATEGORIES:
        scores[category] = st.slider(
            f"{category.capitalize()} · weight {WEIGHTS[category]:.0%}",
            MIN_SCORE,
            MAX_SCORE,
            value=7,
        )

    col_metric, col_button = st.columns([1, 2], vertical_alignment="center")
    col_metric.metric("Overall score", f"{overall_score(scores):.2f}")
    add_clicked = col_button.button("Add to my ranking", type="primary", width="stretch")


# --- Save -------------------------------------------------------------------

if add_clicked:
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
