"""
Interactive charts built with Plotly Express. Every function returns a Plotly
``Figure``; the app shows it with ``st.plotly_chart``.
"""

import plotly.express as px

from vgrank.analysis import scores_long_format
from vgrank.scoring import MAX_SCORE, MIN_SCORE

# One colour is enough: every chart shows a single series.
MAIN_COLOR = "#4F46E5"
DEFAULT_HEIGHT = 380


def apply_style(fig, title, height=DEFAULT_HEIGHT):
    """
    Give every chart the same look: white background, same font, same margins.

    Parameters
    ----------
    fig : plotly.graph_objects.Figure
    title : str
    height : int, optional

    Returns
    -------
    plotly.graph_objects.Figure
        The same figure, restyled.
    """
    fig.update_layout(
        title={"text": title, "x": 0, "font": {"size": 16}},
        template="plotly_white",
        font={"size": 13},
        height=height,
        margin={"l": 10, "r": 10, "t": 50, "b": 10},
        showlegend=False,
    )
    return fig


def category_boxplot(ranking):
    """
    Box plot of the scores given in each category.

    Parameters
    ----------
    ranking : pandas.DataFrame
        Table returned by ``GameCollection.ranking()``.

    Returns
    -------
    plotly.graph_objects.Figure
    """
    long_table = scores_long_format(ranking)

    fig = px.box(
        long_table,
        x="category",
        y="score",
        points="all",  # also draw one dot per game
        hover_name="title",
        color_discrete_sequence=[MAIN_COLOR],
    )
    fig.update_yaxes(range=[MIN_SCORE - 0.5, MAX_SCORE + 0.5], title="Score")
    fig.update_xaxes(title="")
    return apply_style(fig, "Scores given in each category")


def correlation_heatmap(correlation):
    """
    Heatmap of the correlation matrix between categories.

    Parameters
    ----------
    correlation : pandas.DataFrame
        Square matrix returned by ``analysis.category_correlation``.

    Returns
    -------
    plotly.graph_objects.Figure
    """
    fig = px.imshow(
        correlation,
        text_auto=".2f",
        color_continuous_scale="RdBu",  # two colours with a neutral middle for [-1, 1]
        zmin=-1,
        zmax=1,
        aspect="auto",
    )
    fig.update_coloraxes(showscale=False)
    return apply_style(fig, "Correlation between categories")


def genre_bar_chart(genre_table):
    """
    Horizontal bar chart of the average overall score per genre.

    Parameters
    ----------
    genre_table : pandas.DataFrame
        Table returned by ``analysis.score_by_genre`` (genres are the index).

    Returns
    -------
    plotly.graph_objects.Figure
    """
    table = genre_table.reset_index()

    fig = px.bar(
        table,
        x="mean_overall",
        y="genre",
        orientation="h",
        text="mean_overall",
        hover_data={"n_games": True, "mean_overall": ":.2f", "genre": False},
        color_discrete_sequence=[MAIN_COLOR],
    )
    fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
    fig.update_xaxes(range=[0, MAX_SCORE + 1], title="Average overall score")
    fig.update_yaxes(title="", autorange="reversed")  # best genre on top
    return apply_style(fig, "Average score by genre")


def games_per_year_chart(counts):
    """
    Bar chart of the number of rated games per release year.

    Parameters
    ----------
    counts : pandas.Series
        Series returned by ``analysis.games_per_year``.

    Returns
    -------
    plotly.graph_objects.Figure
    """
    table = counts.reset_index()
    table.columns = ["year", "games"]
    table["year"] = table["year"].astype(str)  # years are labels, not numbers

    fig = px.bar(table, x="year", y="games", color_discrete_sequence=[MAIN_COLOR])
    fig.update_xaxes(title="Release year")
    fig.update_yaxes(title="Number of games", dtick=1)
    return apply_style(fig, "Rated games by release year")


def metacritic_scatter(comparison_table):
    """
    Scatter plot of the user's overall score against the Metacritic score.

    Titles appear when hovering a point, so labels never overlap.

    Parameters
    ----------
    comparison_table : pandas.DataFrame
        Table returned by ``analysis.compare_with_metacritic``.

    Returns
    -------
    plotly.graph_objects.Figure
    """
    fig = px.scatter(
        comparison_table,
        x="metacritic_10",
        y="overall",
        hover_name="title",
        hover_data={"metacritic_10": ":.1f", "overall": ":.2f", "difference": ":+.2f"},
        color_discrete_sequence=[MAIN_COLOR],
    )
    fig.update_traces(marker={"size": 12})

    # Zoom on the area where the points actually are (most scores are high).
    lowest = min(comparison_table["metacritic_10"].min(), comparison_table["overall"].min())
    axis_range = [lowest - 0.5, MAX_SCORE + 0.5]

    # The diagonal is where the user and Metacritic agree perfectly.
    fig.add_shape(
        type="line",
        x0=axis_range[0],
        y0=axis_range[0],
        x1=axis_range[1],
        y1=axis_range[1],
        line={"dash": "dash", "color": "gray", "width": 1},
    )
    fig.update_xaxes(range=axis_range, title="Metacritic score (rescaled to 0-10)")
    fig.update_yaxes(range=axis_range, title="My overall score")
    return apply_style(fig, "My scores vs Metacritic", height=450)
