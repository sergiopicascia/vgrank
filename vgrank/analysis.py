"""
Statistics computed on the ranking table.

Every function receives the DataFrame returned by ``GameCollection.ranking()``
and returns a new table or a small dictionary of numbers.
"""

import numpy as np
import pandas as pd
from scipy import stats

from vgrank.scoring import CATEGORIES


def category_summary(ranking):
    """
    Descriptive statistics (mean, std, min, max) for each category.

    Parameters
    ----------
    ranking : pandas.DataFrame

    Returns
    -------
    pandas.DataFrame
        One row per category, columns ``mean``, ``std``, ``min``, ``max``.
    """
    summary = ranking[CATEGORIES].agg(["mean", "std", "min", "max"])
    # ``agg`` puts categories in columns: transpose so that they become rows.
    return summary.T.round(2)


def scores_long_format(ranking):
    """
    Reshape the ranking from wide to long format: one row per (game, category).

    This is the layout that Plotly Express expects for box plots and similar charts.

    Parameters
    ----------
    ranking : pandas.DataFrame

    Returns
    -------
    pandas.DataFrame
        Columns ``title``, ``category`` and ``score``.
    """
    long_table = ranking.melt(
        id_vars=["title"],
        value_vars=CATEGORIES,
        var_name="category",
        value_name="score",
    )
    return long_table


def category_correlation(ranking):
    """
    Pearson correlation between the categories and the overall score.

    Parameters
    ----------
    ranking : pandas.DataFrame

    Returns
    -------
    pandas.DataFrame
        A square correlation matrix.
    """
    return ranking[CATEGORIES + ["overall"]].corr().round(2)


def score_by_genre(ranking, min_games=1):
    """
    Average overall score for each genre.

    A game can have several genres (stored as ``"Action, RPG"``), so the column
    is split and "exploded" to obtain one row per (game, genre) pair first.

    Parameters
    ----------
    ranking : pandas.DataFrame
    min_games : int, optional
        Keep only genres with at least this number of games (default 1).

    Returns
    -------
    pandas.DataFrame
        One row per genre, columns ``mean_overall`` and ``n_games``,
        sorted from the best genre to the worst.
    """
    exploded = ranking.assign(genre=ranking["genres"].str.split(", ")).explode("genre")
    exploded = exploded.dropna(subset=["genre"])

    grouped = exploded.groupby("genre")["overall"].agg(["mean", "count"])
    grouped = grouped.rename(columns={"mean": "mean_overall", "count": "n_games"})
    grouped = grouped[grouped["n_games"] >= min_games]

    return grouped.sort_values("mean_overall", ascending=False).round(2)


def strongest_category(ranking):
    """
    Find, for every game, the category in which it stands out the most.

    Scores are first standardised (z-score) column by column, so that a
    category the user tends to rate high does not always win.

    Parameters
    ----------
    ranking : pandas.DataFrame

    Returns
    -------
    pandas.DataFrame
        Columns ``title``, ``strongest`` (category name) and ``z_score``.
    """
    score_matrix = ranking[CATEGORIES].to_numpy(dtype=float)

    # z = (x - mean) / std, computed for each column. When a column has zero
    # standard deviation scipy returns NaN, which we replace with 0.
    z_scores = stats.zscore(score_matrix, axis=0, ddof=0)
    z_scores = np.nan_to_num(z_scores)

    best_index = np.argmax(z_scores, axis=1)  # position of the max in each row

    return pd.DataFrame(
        {
            "title": ranking["title"],
            "strongest": [CATEGORIES[i] for i in best_index],
            "z_score": np.round(z_scores.max(axis=1), 2),
        }
    )


def compare_with_metacritic(ranking):
    """
    Compare the user's overall score with the Metacritic score (0-100).

    Metacritic is rescaled to 0-10 so that both scores share the same range.
    The agreement between the two is measured with Spearman's rank correlation.

    Parameters
    ----------
    ranking : pandas.DataFrame

    Returns
    -------
    tuple (pandas.DataFrame, dict)
        The table of games that have a Metacritic score, with the extra columns
        ``metacritic_10`` and ``difference`` (user minus Metacritic), and a
        dictionary with ``n_games``, ``correlation`` and ``p_value``.
        Correlation and p-value are ``None`` when there are fewer than 3 games.
    """
    table = ranking.dropna(subset=["metacritic"]).copy()
    table["metacritic_10"] = table["metacritic"] / 10
    table["difference"] = (table["overall"] - table["metacritic_10"]).round(2)

    result = {"n_games": len(table), "correlation": None, "p_value": None}

    if len(table) >= 3:
        correlation, p_value = stats.spearmanr(table["overall"], table["metacritic_10"])
        result["correlation"] = round(float(correlation), 3)
        result["p_value"] = round(float(p_value), 3)

    return table, result


def games_per_year(ranking):
    """
    Count how many rated games were released in each year.

    Parameters
    ----------
    ranking : pandas.DataFrame

    Returns
    -------
    pandas.Series
        Index: year, values: number of games (years with no games are skipped).
    """
    dates = pd.to_datetime(ranking["released"], errors="coerce")
    years = dates.dt.year.dropna().astype(int)
    return years.value_counts().sort_index()
