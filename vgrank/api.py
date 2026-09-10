"""
Search video games on the RAWG API (https://rawg.io/apidocs).

RAWG requires a free API key. The key is read from the ``RAWG_API_KEY``
environment variable, which can also be written in a ``.env`` file placed in
the project folder (see ``.env.example``).
"""

import os

import requests
from dotenv import load_dotenv

BASE_URL = "https://api.rawg.io/api/games"
TIMEOUT_SECONDS = 10


class ApiError(Exception):
    """Raised when the RAWG API cannot be used (missing key, network problem, bad answer)."""


def get_api_key():
    """
    Read the RAWG API key from the environment (or from the ``.env`` file).

    Returns
    -------
    str

    Raises
    ------
    ApiError
        If the key is not set.
    """
    load_dotenv()  # loads the variables written in .env, if the file exists
    key = os.environ.get("RAWG_API_KEY", "")

    if key == "":
        raise ApiError(
            "No RAWG API key found. Get a free key at https://rawg.io/apidocs "
            "and put it in a .env file as RAWG_API_KEY=your_key"
        )
    return key


def parse_game(item):
    """
    Keep only the fields we need from one game returned by the API.

    Parameters
    ----------
    item : dict
        One element of the ``results`` list returned by RAWG.

    Returns
    -------
    dict
        Keys: ``game_id``, ``title``, ``released``, ``genres``, ``platforms``,
        ``metacritic``, ``image_url``.
    """
    genres = [genre["name"] for genre in item.get("genres") or []]
    platforms = [entry["platform"]["name"] for entry in item.get("platforms") or []]

    return {
        "game_id": item["id"],
        "title": item.get("name", ""),
        "released": item.get("released") or "",
        "genres": genres,
        "platforms": platforms,
        "metacritic": item.get("metacritic"),
        "image_url": item.get("background_image") or "",
    }


def search_games(query, max_results=10):
    """
    Search games by name on RAWG.

    Parameters
    ----------
    query : str
        Text to search, for example ``"zelda"``.
    max_results : int, optional
        Maximum number of games to return (default 10).

    Returns
    -------
    list of dict
        One dictionary per game, in the format produced by ``parse_game``.
        The list is empty if nothing matches.

    Raises
    ------
    ApiError
        If the key is missing, the request fails or the answer is not valid JSON.
    """
    params = {
        "key": get_api_key(),
        "search": query,
        "page_size": max_results,
    }

    try:
        response = requests.get(BASE_URL, params=params, timeout=TIMEOUT_SECONDS)
        response.raise_for_status()  # turns HTTP errors (401, 500, ...) into exceptions
    except requests.exceptions.Timeout:
        raise ApiError("The RAWG API did not answer in time, please retry")
    except requests.exceptions.RequestException as error:
        raise ApiError(f"Could not reach the RAWG API: {error}")

    try:
        data = response.json()
    except ValueError:
        raise ApiError("The RAWG API returned an answer that is not valid JSON")

    return [parse_game(item) for item in data.get("results", [])]
