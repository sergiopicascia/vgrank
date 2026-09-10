"""
The ``Game`` class: one video game together with the scores the user gave it.
"""

import pandas as pd

from vgrank.scoring import CATEGORIES, overall_score

# Columns used when a game is turned into a row of a table (or a CSV file).
GAME_COLUMNS = [
    "game_id",
    "title",
    "released",
    "genres",
    "platforms",
    "metacritic",
    "image_url",
] + CATEGORIES


class Game:
    """
    A video game rated by the user.

    Attributes
    ----------
    game_id : int
        Identifier of the game on RAWG (used to avoid duplicates).
    title : str
        Name of the game.
    released : str
        Release date in ``YYYY-MM-DD`` format (empty string if unknown).
    genres : list of str
        Genres of the game, for example ``["Action", "RPG"]``.
    platforms : list of str
        Platforms the game is available on.
    metacritic : float or None
        Metacritic score (0-100) if available, ``None`` otherwise.
    image_url : str
        URL of the cover image (empty string if unknown).
    scores : dict
        Mapping ``category -> score`` given by the user.
    """

    def __init__(self, game_id, title, released, genres, platforms, metacritic, image_url, scores):
        self.game_id = int(game_id)
        self.title = title
        self.released = released
        self.genres = genres
        self.platforms = platforms
        self.metacritic = metacritic
        self.image_url = image_url
        self.scores = scores

    def overall(self):
        """Return the weighted overall score of the game."""
        return overall_score(self.scores)

    def release_year(self):
        """Return the release year as an integer, or ``None`` if unknown."""
        if not self.released:
            return None
        return int(self.released[:4])

    def to_dict(self):
        """
        Convert the game into a flat dictionary, ready to become a table row.

        Lists are stored as comma separated strings so that they fit in a CSV cell.

        Returns
        -------
        dict
            One key for each name in ``GAME_COLUMNS``.
        """
        row = {
            "game_id": self.game_id,
            "title": self.title,
            "released": self.released,
            "genres": ", ".join(self.genres),
            "platforms": ", ".join(self.platforms),
            "metacritic": self.metacritic,
            "image_url": self.image_url,
        }
        for category in CATEGORIES:
            row[category] = self.scores[category]
        return row

    def __repr__(self):
        return f"Game({self.title!r}, overall={self.overall()})"


def text_or_empty(value):
    """Return ``value`` as a string, or an empty string if it is missing (NaN/None)."""
    if value is None or pd.isna(value):
        return ""
    return str(value)


def split_list(value):
    """Turn a comma separated string like ``"Action, RPG"`` into a list of strings."""
    text = text_or_empty(value)
    if text == "":
        return []
    return [item.strip() for item in text.split(",")]


def game_from_row(row):
    """
    Build a ``Game`` from a table row (a dictionary or a pandas Series).

    This is the inverse of ``Game.to_dict``.

    Parameters
    ----------
    row : dict or pandas.Series
        Must contain every name in ``GAME_COLUMNS``.

    Returns
    -------
    Game
    """
    metacritic = row["metacritic"]
    if metacritic is None or pd.isna(metacritic):
        metacritic = None
    else:
        metacritic = float(metacritic)

    scores = {}
    for category in CATEGORIES:
        scores[category] = int(row[category])

    return Game(
        game_id=row["game_id"],
        title=text_or_empty(row["title"]),
        released=text_or_empty(row["released"]),
        genres=split_list(row["genres"]),
        platforms=split_list(row["platforms"]),
        metacritic=metacritic,
        image_url=text_or_empty(row["image_url"]),
        scores=scores,
    )
