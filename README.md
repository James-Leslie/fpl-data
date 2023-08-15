# FPL data loader
Python package for loading and transforming data from the Fantasy Premier Leage API.

## Usage

The package provides two main classes: `FplApiData` and `get_element_summary`.

The `FplApiData` class can be used to download all relevant data from the FPL API, including:

* Players
* Positions
* Teams
* Game weeks
* Fixtures

To use the `FplApiData` class, first create an instance of the class:
```python
from fpl_data.api import FplApiData

# make a request to the FPL API
api_data = FplApiData()
```

Then, you can access the data using the following attributes:

* `elements`: A list of all players in the current season.
* `element_types`: A list of all positions in the FPL game.
* `teams`: A list of all teams in the Premier League.
* `events`: A list of all game weeks in the current season.
* `fixtures`: A list of all fixtures in the current season.

For example, to get the list of all players in the current season, you would do the following:
```python
players = data.elements
```

The `get_element_summary` function can be used to get all past gameweek/season info for a given player_id.

To use the `get_element_summary` function, you need to pass the `player_id` as an argument:
```python
summary = get_element_summary(player_id)
```

The `summary` object will contain the following information:

* `history`: A list of all gameweek data for the current season.
* `history_past`: A list of all gameweek data for past seasons.

For example, to get all past gameweek/season info for the player with ID 1, you would do the following:
```python
summary = get_element_summary(1000)
```

The `history` attribute of the summary object will contain a list of dictionaries, each of which representing a gameweek. The dictionaries will contain the following keys:

* `gameweek`: The gameweek number.
* `points`: The number of points the player scored in the gameweek.
* `minutes`: The number of minutes the player played in the gameweek.
* `goals_scored`: The number of goals the player scored in the gameweek.
* `assists`: The number of assists the player provided in the gameweek.
* `clean_sheets`: The number of clean sheets the player kept in the gameweek.
* `bonus`: The bonus points the player earned in the gameweek.
* `red_card`: A boolean value indicating whether the player was sent off in the gameweek.

The `history_past` attribute of the summary object will contain a list of dictionaries, each of which representing a gameweek from a past season. The dictionaries will contain the same keys as the history attribute.

---
## Local development
Make a virtual environment
```bash
cd fpl-data
conda env create -f environment.yml --prefix ./.env
```

Activate your environemt with:
```bash
conda activate ./.env
```

Create an editable install of the package
```bash
pip install --editable .
```