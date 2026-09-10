"""
Charts for the ranking. Every function returns a matplotlib ``Figure`` so that
the caller decides what to do with it (show it in Streamlit, save it to disk...).
"""

import matplotlib.pyplot as plt
import seaborn as sns

from vgrank.analysis import scores_long_format
from vgrank.scoring import MAX_SCORE, MIN_SCORE

# One colour is enough: every chart shows a single series.
MAIN_COLOR = "#4C72B0"


def ranking_bar_chart(ranking, top_n=10):
    """
    Horizontal bar chart of the best ``top_n`` games.

    Parameters
    ----------
    ranking : pandas.DataFrame
        Table returned by ``GameCollection.ranking()``.
    top_n : int, optional
        Number of games to show (default 10).

    Returns
    -------
    matplotlib.figure.Figure
    """
    top = ranking.head(top_n).iloc[::-1]  # reversed so that the best game is on top

    fig, ax = plt.subplots(figsize=(8, 0.45 * len(top) + 1))
    ax.barh(top["title"], top["overall"], color=MAIN_COLOR)

    for position, value in enumerate(top["overall"]):
        ax.text(value + 0.1, position, f"{value:.2f}", va="center", fontsize=9)

    ax.set_xlim(0, MAX_SCORE + 1)
    ax.set_xlabel("Overall score")
    ax.set_title(f"Top {len(top)} games")
    sns.despine(fig)
    fig.tight_layout()
    return fig


def category_boxplot(ranking):
    """
    Box plot of the scores given in each category.

    Parameters
    ----------
    ranking : pandas.DataFrame

    Returns
    -------
    matplotlib.figure.Figure
    """
    long_table = scores_long_format(ranking)

    fig, ax = plt.subplots(figsize=(8, 4))
    sns.boxplot(data=long_table, x="category", y="score", color=MAIN_COLOR, ax=ax)

    ax.set_ylim(MIN_SCORE - 0.5, MAX_SCORE + 0.5)
    ax.set_xlabel("")
    ax.set_ylabel("Score")
    ax.set_title("How scores are distributed in each category")
    sns.despine(fig)
    fig.tight_layout()
    return fig


def correlation_heatmap(correlation):
    """
    Heatmap of the correlation matrix between categories.

    Parameters
    ----------
    correlation : pandas.DataFrame
        Square matrix returned by ``analysis.category_correlation``.

    Returns
    -------
    matplotlib.figure.Figure
    """
    fig, ax = plt.subplots(figsize=(7, 5))
    sns.heatmap(
        correlation,
        annot=True,
        fmt=".2f",
        cmap="RdBu",  # two colours with a neutral middle: good for values in [-1, 1]
        vmin=-1,
        vmax=1,
        square=True,
        ax=ax,
    )
    ax.set_title("Correlation between categories")
    fig.tight_layout()
    return fig


def genre_bar_chart(genre_table):
    """
    Bar chart of the average overall score per genre.

    Parameters
    ----------
    genre_table : pandas.DataFrame
        Table returned by ``analysis.score_by_genre``.

    Returns
    -------
    matplotlib.figure.Figure
    """
    fig, ax = plt.subplots(figsize=(8, 0.4 * len(genre_table) + 1))
    ax.barh(genre_table.index, genre_table["mean_overall"], color=MAIN_COLOR)

    for position, (value, count) in enumerate(
        zip(genre_table["mean_overall"], genre_table["n_games"])
    ):
        ax.text(value + 0.1, position, f"{value:.2f} ({count} games)", va="center", fontsize=9)

    ax.invert_yaxis()  # best genre on top
    ax.set_xlim(0, MAX_SCORE + 2)
    ax.set_xlabel("Average overall score")
    ax.set_title("Average score by genre")
    sns.despine(fig)
    fig.tight_layout()
    return fig


def metacritic_scatter(comparison_table):
    """
    Scatter plot of the user's overall score against the Metacritic score.

    Parameters
    ----------
    comparison_table : pandas.DataFrame
        Table returned by ``analysis.compare_with_metacritic``.

    Returns
    -------
    matplotlib.figure.Figure
    """
    fig, ax = plt.subplots(figsize=(7, 6))

    ax.scatter(
        comparison_table["metacritic_10"],
        comparison_table["overall"],
        color=MAIN_COLOR,
        s=60,
    )
    for _, row in comparison_table.iterrows():
        ax.annotate(
            row["title"],
            (row["metacritic_10"], row["overall"]),
            fontsize=8,
            xytext=(5, 3),
            textcoords="offset points",
        )

    # The diagonal is where the user and Metacritic agree perfectly.
    ax.plot(
        [MIN_SCORE, MAX_SCORE],
        [MIN_SCORE, MAX_SCORE],
        linestyle="--",
        color="gray",
        linewidth=1,
        label="Perfect agreement",
    )

    # Zoom on the area where the points actually are (most scores are high).
    lowest = min(comparison_table["metacritic_10"].min(), comparison_table["overall"].min())
    ax.set_xlim(lowest - 0.5, MAX_SCORE + 0.5)
    ax.set_ylim(lowest - 0.5, MAX_SCORE + 0.5)
    ax.set_xlabel("Metacritic score (rescaled to 0-10)")
    ax.set_ylabel("My overall score")
    ax.set_title("My scores vs Metacritic")
    ax.legend(loc="lower right")
    sns.despine(fig)
    fig.tight_layout()
    return fig


def games_per_year_chart(counts):
    """
    Bar chart of the number of rated games per release year.

    Parameters
    ----------
    counts : pandas.Series
        Series returned by ``analysis.games_per_year``.

    Returns
    -------
    matplotlib.figure.Figure
    """
    fig, ax = plt.subplots(figsize=(8, 3.5))
    ax.bar(counts.index.astype(str), counts.values, color=MAIN_COLOR)

    ax.set_xlabel("Release year")
    ax.set_ylabel("Number of games")
    ax.set_title("Rated games by release year")
    ax.yaxis.get_major_locator().set_params(integer=True)
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
    sns.despine(fig)
    fig.tight_layout()
    return fig
