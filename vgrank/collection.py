"""
The ``GameCollection`` class: the list of rated games, saved to a CSV file.
"""

import os

import pandas as pd

from vgrank.models import GAME_COLUMNS, game_from_row
from vgrank.scoring import add_overall_column, rank_games

# Path of the CSV file used when no other path is given.
DEFAULT_CSV_PATH = os.path.join("data", "games.csv")


class GameCollection:
    """
    A collection of rated games stored in a CSV file.

    Every change (add, remove) is immediately written to disk, so the
    collection survives between runs of the application.

    Attributes
    ----------
    csv_path : str
        Path of the CSV file used to load and save the games.
    games : list of Game
        The games currently in the collection.
    """

    def __init__(self, csv_path=DEFAULT_CSV_PATH):
        self.csv_path = csv_path
        self.games = []

    def load(self):
        """
        Read the games from the CSV file.

        A missing or empty file is not an error: the collection simply starts empty.

        Returns
        -------
        GameCollection
            The collection itself, so that ``GameCollection().load()`` works.
        """
        self.games = []

        if not os.path.exists(self.csv_path):
            return self

        try:
            table = pd.read_csv(self.csv_path)
        except pd.errors.EmptyDataError:
            return self

        for _, row in table.iterrows():
            self.games.append(game_from_row(row))

        return self

    def save(self):
        """Write the collection to the CSV file (the folder is created if needed)."""
        folder = os.path.dirname(self.csv_path)
        if folder != "":
            os.makedirs(folder, exist_ok=True)

        self.to_dataframe().to_csv(self.csv_path, index=False)

    def contains(self, game_id):
        """Return ``True`` if a game with this ``game_id`` is already in the collection."""
        for game in self.games:
            if game.game_id == game_id:
                return True
        return False

    def add(self, game):
        """
        Add a game to the collection and save the file.

        Parameters
        ----------
        game : Game

        Raises
        ------
        ValueError
            If a game with the same ``game_id`` is already present.
        """
        if self.contains(game.game_id):
            raise ValueError(f"'{game.title}' is already in the collection")

        self.games.append(game)
        self.save()

    def remove(self, game_id):
        """
        Remove the game with the given ``game_id`` and save the file.

        Parameters
        ----------
        game_id : int

        Raises
        ------
        ValueError
            If no game has that ``game_id``.
        """
        if not self.contains(game_id):
            raise ValueError(f"No game with id {game_id} in the collection")

        self.games = [game for game in self.games if game.game_id != game_id]
        self.save()

    def to_dataframe(self):
        """
        Convert the collection into a pandas DataFrame with one row per game.

        Returns
        -------
        pandas.DataFrame
            Columns are ``GAME_COLUMNS``; the table is empty if there are no games.
        """
        rows = [game.to_dict() for game in self.games]
        return pd.DataFrame(rows, columns=GAME_COLUMNS)

    def ranking(self):
        """
        Build the ranking table: games sorted by overall score.

        Returns
        -------
        pandas.DataFrame
            The collection table with the extra ``overall`` and ``rank`` columns.
        """
        table = add_overall_column(self.to_dataframe())
        return rank_games(table)

    def __len__(self):
        return len(self.games)
