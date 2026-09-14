"""
Page "Insights": statistics and interactive charts about the rated games.
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

tab_categories, tab_genres, tab_critics = st.tabs(["Categories", "Genres and years", "Vs critics"])


# --- Categories -------------------------------------------------------------

with tab_categories:
    col_box, col_heatmap = st.columns(2)
    with col_box:
        st.plotly_chart(plots.category_boxplot(ranking), width="stretch")
    with col_heatmap:
        st.plotly_chart(
            plots.correlation_heatmap(analysis.category_correlation(ranking)), width="stretch"
        )

    col_summary, col_strongest = st.columns(2)
    with col_summary:
        st.markdown("**Summary of the scores in each category**")
        st.dataframe(
            analysis.category_summary(ranking).rename(columns=str.capitalize), width="stretch"
        )
    with col_strongest:
        st.markdown("**Where each game stands out** (highest z-score)")
        st.dataframe(
            analysis.strongest_category(ranking).rename(
                columns={"title": "Game", "strongest": "Category", "z_score": "z-score"}
            ),
            hide_index=True,
            width="stretch",
        )


# --- Genres and years -------------------------------------------------------

with tab_genres:
    min_games = st.slider("Show genres with at least this many games", 1, 5, 2)
    genre_table = analysis.score_by_genre(ranking, min_games=min_games)

    col_genres, col_years = st.columns(2)
    with col_genres:
        if len(genre_table) == 0:
            st.warning("No genre has that many games.")
        else:
            st.plotly_chart(plots.genre_bar_chart(genre_table), width="stretch")
    with col_years:
        st.plotly_chart(
            plots.games_per_year_chart(analysis.games_per_year(ranking)), width="stretch"
        )


# --- Metacritic -------------------------------------------------------------

with tab_critics:
    comparison, summary = analysis.compare_with_metacritic(ranking)

    if summary["correlation"] is None:
        st.info("At least 3 games with a Metacritic score are needed for this section.")
    else:
        col_n, col_corr, col_p = st.columns(3)
        col_n.metric("Games with a Metacritic score", summary["n_games"])
        col_corr.metric("Spearman correlation", f"{summary['correlation']:.2f}")
        col_p.metric("p-value", f"{summary['p_value']:.3f}")

        col_scatter, col_table = st.columns([3, 2], vertical_alignment="center")
        with col_scatter:
            st.plotly_chart(plots.metacritic_scatter(comparison), width="stretch")
        with col_table:
            st.markdown("**Biggest disagreements** (my score minus Metacritic, both 0-10)")
            order = comparison["difference"].abs().sort_values(ascending=False).index
            top_differences = comparison.loc[order].head(5)
            st.dataframe(
                top_differences[["title", "overall", "metacritic_10", "difference"]].rename(
                    columns={
                        "title": "Game",
                        "overall": "Mine",
                        "metacritic_10": "Metacritic",
                        "difference": "Difference",
                    }
                ),
                hide_index=True,
                width="stretch",
            )
