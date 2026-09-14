# 🎮 VideoGame Ranking

VideoGame Ranking lets you search video games, rate them in five categories and 
build a personal ranking that you can explore in a web app.

![Streamlit app](https://img.shields.io/badge/built%20with-Streamlit-ff4b4b)
![Python](https://img.shields.io/badge/python-3.11%2B-blue)

## What the app does

The app has three pages:

| Page | What you can do |
|------|-----------------|
| **Ranking** (`pages/ranking.py`) | The leaderboard: a podium for the first three games and a row for every other game, with filters by genre and minimum score. Every game has an *Edit* button to change its scores or remove it. The ranking can be downloaded as CSV. |
| **Add game** (`pages/add_game.py`) | Search a title on the RAWG API, pick the right game, rate it with five sliders and add it to the ranking. |
| **Insights** (`pages/insights.py`) | Interactive charts and statistics: score distribution per category, correlation between categories, best genres, games per year, agreement with Metacritic. |

### How the score works

Each game is rated from 1 to 10 in five categories. The **overall score** is a
weighted average:

| Category | Weight |
|----------|--------|
| Gameplay | 30 % |
| Story | 20 % |
| Graphics | 20 % |
| Sound | 10 % |
| Replayability | 20 % |

Categories and weights live in one place, [`vgrank/scoring.py`](vgrank/scoring.py),
so they are easy to change.

## Data sources

- **[RAWG Video Games Database API](https://rawg.io/apidocs)**: used to search games
  and to get their release date, genres, platforms, cover image and Metacritic score.
  A free API key is required (see *Setup*).
- **`data/games.csv`**: the local file where the rated games are saved. The
  repository already contains 15 rated games, so the ranking is not empty at the
  first run. Delete the rows (keep the header) to start from scratch.

## Libraries

| Library | Used for |
|---------|----------|
| `requests` | calling the RAWG API |
| `python-dotenv` | reading the API key from the `.env` file |
| `pandas` | storing, reshaping and filtering the games table |
| `numpy` | weighted averages and array operations |
| `scipy` | z-scores and Spearman correlation |
| `plotly` | interactive charts |
| `streamlit` | the web application |

Exact versions are listed in [`requirements.txt`](requirements.txt).

## Setup

1. Clone the repository and enter the folder:

   ```bash
   git clone https://github.com/<your-user>/vgrank.git
   cd vgrank
   ```

2. Create a virtual environment and install the dependencies (Python 3.11 or newer):

   ```bash
   python -m venv .venv
   source .venv/bin/activate        # on Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Get a free API key at <https://rawg.io/apidocs>, copy `.env.example` to `.env`
   and paste the key inside:

   ```bash
   cp .env.example .env
   # then edit .env so that it reads: RAWG_API_KEY=your_key
   ```

   The `.env` file is listed in `.gitignore`, so the key is never pushed to GitHub.
   Without a key the Ranking and Insights pages still work, only the search does not.

## Run

Start the web app:

```bash
streamlit run app.py
```

The browser opens at <http://localhost:8501>. Use the sidebar to move between pages.

The backend can also be used without Streamlit, like any library:

```python
from vgrank.collection import GameCollection

collection = GameCollection().load()
print(collection.ranking()[["rank", "title", "overall"]])
```

## Project structure

```
vgrank/
├── app.py                  # Streamlit entry point: declares the pages
├── pages/
│   ├── ranking.py          # the leaderboard, with edit/remove dialog
│   ├── add_game.py         # search on RAWG + rate + save
│   └── insights.py         # statistics and charts
├── vgrank/                 # the backend package (no Streamlit code here)
│   ├── __init__.py
│   ├── api.py              # RAWG API calls and error handling
│   ├── models.py           # the Game class
│   ├── collection.py       # the GameCollection class (CSV load/save, ranking)
│   ├── scoring.py          # categories, weights, overall score
│   ├── analysis.py         # statistics with pandas, numpy and scipy
│   └── plots.py            # interactive charts with plotly
├── data/
│   └── games.csv           # the rated games
├── .streamlit/config.toml  # colours and font of the app
├── .env.example            # template for the API key
├── .gitignore
├── requirements.txt
└── README.md
```

Everything in `vgrank/` is plain Python that could be
reused in a notebook or a script, while `app.py` and `pages/` only deal with
showing things on screen.