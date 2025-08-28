# Fantasy Premier League (FPL) Public API Reference

The FPL API is undocumented but publicly accessible. These endpoints provide the data that powers the official FPL website and app.

**Base URL:**

    https://fantasy.premierleague.com/api/

## Main Endpoints

### `bootstrap-static/`
- **Description:** Main endpoint. Returns a large JSON with season-wide static data.
- **Top-level fields:**
  - `element_stats`: Definitions of the various stats tracked
  - `element_types`: Player positions and rules related to squad selection
  - `elements`: Individual player data
  - `teams`: Details of teams, including some basic stats, such as form and strength
  - `events`: Gameweek info
  - `chips`: Available chips (wildcard, free hit, etc.)
  - `phases`: Months and which gameweeks fall into them
  - `game_config` and `game_settings`: FPL game rules
  - `total_players`: Total number of players in the game

### `element-summary/{player_id}/`
- **Description:** Returns detailed history for a single player.
- **Top-level fields:**
  - `history`: Per-gameweek stats for the current season
  - `history_past`: Per-season stats for previous seasons

### `fixtures/`
- **Description:** List of all fixtures for the season, including scores and kickoff times.

### `event/{event_id}/live/`
- **Description:** Live stats for a specific gameweek (`event_id`).

### `entry/{entry_id}/`
- **Description:** Info about a specific user's team (public data only).

### `entry/{entry_id}/event/{event_id}/picks/`
- **Description:** Squad picks for a user's team in a specific gameweek.

---

**Note:**
All endpoints are public and require no authentication, but excessive requests may result in rate limiting.
