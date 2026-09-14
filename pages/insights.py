"""
Page "Insights": statistics and charts about the rated games.
"""

import streamlit as st

from vgrank import analysis, plots
from vgrank.collection import GameCollection


st.title("Insights")

collection = GameCollection().load()
ranking = collection.ranking()

if len(ranking) < 3:
    st.info("Rate at least 3 games to unlock the statistics.")
    st.stop()


# --- Categories -------------------------------------------------------------

st.header("How do I rate?")

col_table, col_plot = st.columns([1, 2])
with col_table:
    st.write("Summary of the scores given in each category:")
    st.dataframe(analysis.category_summary(ranking), width="stretch")
with col_plot:
    st.pyplot(plots.category_boxplot(ranking))

st.write(
    "Correlation between categories: values close to 1 mean that when a game "
    "scores high in one category it tends to score high in the other too."
)
st.pyplot(plots.correlation_heatmap(analysis.category_correlation(ranking)))

st.write("The category in which each game stands out the most (based on z-scores):")
st.dataframe(analysis.strongest_category(ranking), hide_index=True, width="stretch")


# --- Genres and years -------------------------------------------------------

st.header("Genres and years")

min_games = st.slider("Show genres with at least this many games", 1, 5, 2)
genre_table = analysis.score_by_genre(ranking, min_games=min_games)
if len(genre_table) == 0:
    st.warning("No genre has that many games.")
else:
    st.pyplot(plots.genre_bar_chart(genre_table))

st.pyplot(plots.games_per_year_chart(analysis.games_per_year(ranking)))


# --- Metacritic -------------------------------------------------------------

st.header("Do I agree with the critics?")

comparison, summary = analysis.compare_with_metacritic(ranking)

if summary["correlation"] is None:
    st.info("At least 3 games with a Metacritic score are needed for this section.")
else:
    col_n, col_corr, col_p = st.columns(3)
    col_n.metric("Games with a Metacritic score", summary["n_games"])
    col_corr.metric("Spearman correlation", f"{summary['correlation']:.2f}")
    col_p.metric("p-value", f"{summary['p_value']:.3f}")

    st.pyplot(plots.metacritic_scatter(comparison))

    st.write("Biggest disagreements (my score minus Metacritic, both on a 0-10 scale):")
    order = comparison["difference"].abs().sort_values(ascending=False).index
    st.dataframe(
        comparison.loc[order, ["title", "overall", "metacritic_10", "difference"]].head(5),
        hide_index=True,
        width="stretch",
    )


# --- Export -----------------------------------------------------------------

st.header("Export")
st.download_button(
    "Download the ranking as CSV",
    data=ranking.to_csv(index=False),
    file_name="my_ranking.csv",
    mime="text/csv",
)
