"""
vgrank - a small library to rate video games and build a personal ranking.

The package is organised in modules, each one with a single responsibility:

- ``api``        : search video games on the RAWG web API
- ``models``     : the ``Game`` class that represents one rated game
- ``scoring``    : score categories, weights and the overall score formula
- ``collection`` : the ``GameCollection`` class that stores games in a CSV file
- ``analysis``   : statistics computed on the collection (pandas, numpy, scipy)
- ``plots``      : charts built with matplotlib and seaborn
"""

__version__ = "0.1.0"
