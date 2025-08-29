# API Reference

Complete reference for all FPL Data classes and functions.

## `fpl_data_loader.load`

Raw JSON data from the FPL API.

### `FplApiDataRaw`

Main class for accessing raw FPL data.

```python
from fpl_data.load import FplApiDataRaw

data = FplApiDataRaw()
```

#### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `elements_json` | `list[dict]` | All players with season stats |
| `element_types_json` | `list[dict]` | Position definitions (GK, DEF, MID, FWD) |
| `teams_json` | `list[dict]` | All Premier League teams |
| `events_json` | `list[dict]` | All gameweeks in current season |
| `fixtures_json` | `list[dict]` | All fixtures (past and future) |

#### Key Fields in `elements_json`
- `id`: Player ID
- `web_name`: Display name (e.g., "Haaland")
- `team`: Team ID (1-20)
- `element_type`: Position ID (1=GK, 2=DEF, 3=MID, 4=FWD)
- `total_points`: Season points total
- `now_cost`: Current price (in tenths, e.g., 120 = £12.0m)
- `form`: Recent form rating
- `goals_scored`, `assists`, `clean_sheets`: Season totals

### `get_element_summary(player_id)`

Get detailed history for a specific player.

```python
from fpl_data.load import get_element_summary

summary = get_element_summary(player_id=123)
```

#### Parameters
- `player_id` (`int`): The player's ID from `elements_json`

#### Returns
Dictionary with:
- `history` (`list[dict]`): Current season gameweek data
- `history_past` (`list[dict]`): Previous seasons summary
- `fixtures` (`list[dict]`): Upcoming fixtures

#### `history` Fields (per gameweek)
- `round`: Gameweek number
- `total_points`: Points scored that week
- `minutes`: Minutes played
- `goals_scored`, `assists`, `clean_sheets`: Week totals
- `bonus`: Bonus points
- `bps`: Bonus points system score

---

## `fpl_data_loader.transform`

Cleaned pandas DataFrames with enhanced data.

### `FplApiDataTransformed`

Main class for transformed data.

```python
from fpl_data.transform import FplApiDataTransformed

data = FplApiDataTransformed()
```

#### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `players_df` | `pd.DataFrame` | Enhanced player statistics |
| `teams_df` | `pd.DataFrame` | Team information |
| `gameweeks_df` | `pd.DataFrame` | Gameweek schedule |
| `positions_df` | `pd.DataFrame` | Position definitions |

### Enhanced Columns

The transformed data adds these calculated fields:

#### `players_df` Enhancements
- `GI` (`int`): Goal Involvements = `goals_scored` + `assists`
- `Pts90` (`float`): Points per 90 minutes = `total_points` / (`minutes` / 90)
- Renamed columns match FPL website (e.g., `web_name` → `Name`)
- Proper data types (strings, floats, integers)

#### Key `players_df` Columns
| Column | Type | Description |
|--------|------|-------------|
| `web_name` | `str` | Player display name |
| `team` | `int` | Team ID (1-20) |
| `element_type` | `int` | Position (1=GK, 2=DEF, 3=MID, 4=FWD) |
| `total_points` | `int` | Season points |
| `now_cost` | `int` | Current price (tenths of millions) |
| `form` | `str` | Form rating |
| `GI` | `int` | Goals + Assists |
| `Pts90` | `float` | Points per 90 minutes |

## Data Types Reference

### Team IDs
Teams are referenced by ID (1-20). Use `teams_df` to map IDs to names.

### Position IDs  
- `1`: Goalkeeper
- `2`: Defender  
- `3`: Midfielder
- `4`: Forward

### Price Format
Prices in `now_cost` are in tenths of millions:
- `120` = £12.0m
- `55` = £5.5m

### Form Rating
String representation of recent performance average (e.g., "8.2", "5.0")