"""
Page "Ranking": the leaderboard, with a podium for the first three games and
an edit dialog (change scores or remove) for every game.
"""

import streamlit as st

from vgrank.collection import GameCollection
from vgrank.scoring import CATEGORIES, MAX_SCORE, MIN_SCORE, overall_score

MEDALS = ["🥇", "🥈", "🥉"]

st.title("VideoGame Ranking")

collection = GameCollection().load()
ranking = collection.ranking()

if len(ranking) == 0:
    st.info("The ranking is empty. Open the **Add game** page to search a game and rate it.")
    st.stop()


# --- Helper functions -------------------------------------------------------


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


def show_cover(url, height):
    """Show a cover image cropped to a fixed height, so that all cards line up."""
    if url == "":
        return
    st.markdown(
        f'<img src="{url}" style="width:100%; height:{height}px; '
        f'object-fit:cover; border-radius:8px;">',
        unsafe_allow_html=True,
    )


def describe(row):
    """Return a short caption like ``2015 · Action, RPG`` for a ranking row."""
    year = row["released"][:4] if row["released"] else "n/a"
    return f"{year} · {row['genres']}"


@st.dialog("Edit scores")
def edit_game(row):
    """Open a dialog where the scores of one game can be changed or the game removed."""
    st.subheader(row["title"])

    new_scores = {}
    for category in CATEGORIES:
        new_scores[category] = st.slider(
            category.capitalize(), MIN_SCORE, MAX_SCORE, int(row[category])
        )

    st.metric("New overall score", f"{overall_score(new_scores):.2f}")

    col_save, col_remove = st.columns(2)
    if col_save.button("Save", type="primary", width="stretch"):
        collection.update_scores(int(row["game_id"]), new_scores)
        st.rerun()  # close the dialog and refresh the ranking
    if col_remove.button("Remove from ranking", width="stretch"):
        collection.remove(int(row["game_id"]))
        st.rerun()


def show_podium_card(row):
    """Show one of the first three games as a big card."""
    with st.container(border=True, height="stretch"):
        show_cover(row["image_url"], height=180)
        st.subheader(f"{MEDALS[row['rank'] - 1]} {row['title']}")
        st.caption(describe(row))

        col_score, col_button = st.columns([2, 1], vertical_alignment="center")
        col_score.metric("Overall", f"{row['overall']:.2f}")
        if col_button.button("Edit", key=f"edit_{row['game_id']}", width="stretch"):
            edit_game(row)


def show_ranking_row(row):
    """Show one game as a compact row of the leaderboard."""
    with st.container(border=True):
        col_rank, col_image, col_info, col_scores, col_button = st.columns(
            [0.5, 1.2, 3, 3.5, 1], vertical_alignment="center"
        )
        col_rank.markdown(f"### {row['rank']}")
        with col_image:
            show_cover(row["image_url"], height=70)
        col_info.markdown(f"**{row['title']}**")
        col_info.caption(describe(row))

        details = " · ".join(f"{c.capitalize()} {int(row[c])}" for c in CATEGORIES)
        col_scores.markdown(f"### {row['overall']:.2f}")
        col_scores.caption(details)

        if col_button.button("Edit", key=f"edit_{row['game_id']}", width="stretch"):
            edit_game(row)


# --- Sidebar: filters -------------------------------------------------------

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

st.caption(f"{len(filtered)} games · average overall score {filtered['overall'].mean():.2f}")


# --- Podium -----------------------------------------------------------------

podium = filtered.head(3)
podium_columns = st.columns(len(podium))
for column, (_, row) in zip(podium_columns, podium.iterrows()):
    with column:
        show_podium_card(row)


# --- The rest of the ranking ------------------------------------------------

for _, row in filtered.iloc[3:].iterrows():
    show_ranking_row(row)


# --- Export -----------------------------------------------------------------

st.divider()
st.download_button(
    "Download the ranking as CSV",
    data=ranking.to_csv(index=False),
    file_name="my_ranking.csv",
    mime="text/csv",
)
