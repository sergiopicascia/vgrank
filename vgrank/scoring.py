"""
Scoring rules: the categories a game is rated on, the weight of each category
and the formula that turns the single scores into one overall score.
"""

import numpy as np
import pandas as pd

# The categories a user rates. Every score goes from MIN_SCORE to MAX_SCORE.
CATEGORIES = ["gameplay", "story", "graphics", "sound", "replayability"]

# How much each category counts in the overall score. The weights sum to 1.
WEIGHTS = {
    "gameplay": 0.30,
    "story": 0.20,
    "graphics": 0.20,
    "sound": 0.10,
    "replayability": 0.20,
}

MIN_SCORE = 1
MAX_SCORE = 10


def validate_scores(scores):
    """
    Check that a dictionary of scores is complete and within the allowed range.

    Parameters
    ----------
    scores : dict
        Mapping ``category -> score``, for example ``{"gameplay": 8, ...}``.

    Raises
    ------
    ValueError
        If a category is missing or a score is outside ``[MIN_SCORE, MAX_SCORE]``.
    """
    for category in CATEGORIES:
        if category not in scores:
            raise ValueError(f"Missing score for category '{category}'")

        value = scores[category]
        if value < MIN_SCORE or value > MAX_SCORE:
            raise ValueError(
                f"Score for '{category}' must be between {MIN_SCORE} and {MAX_SCORE}, got {value}"
            )


def overall_score(scores, weights=WEIGHTS):
    """
    Compute the weighted average of the category scores.

    Parameters
    ----------
    scores : dict
        Mapping ``category -> score``.
    weights : dict, optional
        Mapping ``category -> weight``. Defaults to ``WEIGHTS``.

    Returns
    -------
    float
        The overall score, rounded to two decimals.
    """
    validate_scores(scores)

    # Build two arrays in the same category order, then let numpy do the math.
    values = np.array([scores[category] for category in CATEGORIES])
    weight_values = np.array([weights[category] for category in CATEGORIES])

    return round(float(np.average(values, weights=weight_values)), 2)


def add_overall_column(games_df, weights=WEIGHTS):
    """
    Add an ``overall`` column to a DataFrame that has one column per category.

    Parameters
    ----------
    games_df : pandas.DataFrame
        A table with one row per game and the columns listed in ``CATEGORIES``.
    weights : dict, optional
        Mapping ``category -> weight``. Defaults to ``WEIGHTS``.

    Returns
    -------
    pandas.DataFrame
        A copy of the input with the extra ``overall`` column.
    """
    result = games_df.copy()

    if len(result) == 0:
        result["overall"] = pd.Series(dtype=float)
        return result

    # A 2D array with one row per game and one column per category.
    score_matrix = result[CATEGORIES].to_numpy(dtype=float)
    weight_values = np.array([weights[category] for category in CATEGORIES])

    # np.average along axis=1 computes one weighted average per row.
    result["overall"] = np.round(np.average(score_matrix, axis=1, weights=weight_values), 2)
    return result


def rank_games(games_df):
    """
    Sort games from best to worst and add a ``rank`` column starting at 1.

    Parameters
    ----------
    games_df : pandas.DataFrame
        A table with an ``overall`` column (see ``add_overall_column``).

    Returns
    -------
    pandas.DataFrame
        The sorted table with ``rank`` as first column.
    """
    ranked = games_df.sort_values(["overall", "title"], ascending=[False, True])
    ranked = ranked.reset_index(drop=True)
    ranked.insert(0, "rank", np.arange(1, len(ranked) + 1))
    return ranked
