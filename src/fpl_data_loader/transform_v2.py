from typing import Optional, Set

import pandas as pd

from fpl_data_loader.load import FplDataLoader


class FplDataTransformer(FplDataLoader):
    """Clean, maintainable FPL data transformer with compact/full modes.

    Transforms raw FPL API data into clean pandas DataFrames with user-friendly
    column names. Supports both compact mode (essential columns) and full mode
    (all useful columns) for different use cases.
    """

    def __init__(self, compact: bool = True) -> None:
        """Initialize transformer and create clean DataFrames.

        Args:
            compact (bool): If True, return only essential columns for fantasy analysis.
                          If False, return all useful columns for detailed analysis.
        """
        super().__init__()
        self.compact = compact

        # Transform all data types
        self.players_df = self._transform_players()
        self.teams_df = self._transform_teams()
        self.positions_df = self._transform_positions()
        self.gameweeks_df = self._transform_gameweeks()

        # Calculate current season and next gameweek
        self.season = self._get_current_season()
        self.next_gw = self._get_next_gameweek()

    def _get_current_season(self) -> str:
        """Extract current season from first gameweek deadline."""
        first_deadline = self.events_json[0]["deadline_time"]
        year = first_deadline[:4]
        return f"{year}-{str(int(year) + 1)[-2:]}"

    def _get_next_gameweek(self) -> int:
        """Find the next upcoming gameweek."""
        for event in self.events_json:
            if event["is_next"]:
                return event["id"]
        return 1

    def _clean_columns(
        self, df: pd.DataFrame, essential_cols: Optional[Set[str]] = None
    ) -> pd.DataFrame:
        """Clean DataFrame columns: rename, exclude unwanted, select based on mode.

        Args:
            df: DataFrame to clean
            essential_cols: Set of essential column names for compact mode

        Returns:
            Cleaned DataFrame with appropriate columns
        """
        # Column renames
        renames = {
            "id": "player_id",
            "team": "team_id",
            "element_type": "position_id",
            "second_name": "last_name",
            "web_name": "short_name",
            "now_cost": "price",
            "minutes": "minutes_played",
            "bonus": "bonus_points",
        }

        # Columns to always exclude
        exclude_cols = {
            "code",
            "pulse_id",
            "team_division",
            "photo",
            "status",
            "chance_of_playing_this_round",
            "chance_of_playing_next_round",
            "element_stats",
            "game_settings",
            "total_players",
            "phases",
        }

        # Apply renames
        df = df.rename(columns=renames)

        # Remove unwanted columns
        df = df.drop([col for col in exclude_cols if col in df.columns], axis=1)

        # Select columns based on mode
        if self.compact and essential_cols:
            available_essential = [col for col in essential_cols if col in df.columns]
            df = df[available_essential]

        return df

    def _transform_players(self) -> pd.DataFrame:
        """Transform raw player data into clean DataFrame."""
        essential_cols = {
            "player_id",
            "player_name",
            "first_name",
            "last_name",
            "team_id",
            "position_id",
            "price",
            "total_points",
            "minutes_played",
            "goals_scored",
            "assists",
            "expected_goals",
            "expected_assists",
            "clean_sheets",
            "points_per_game",
            "selected_by_percent",
        }

        # Start with raw data
        df = pd.DataFrame(self.elements_json)

        # Clean columns
        df = self._clean_columns(df, essential_cols)

        # Convert price from API format (e.g., 100 -> 10.0)
        if "price" in df.columns:
            df["price"] = df["price"] / 10

        # Convert data types
        float_cols = [
            "points_per_game",
            "expected_goals",
            "expected_assists",
            "expected_goal_involvements",
            "expected_goals_conceded",
            "influence",
            "creativity",
            "threat",
            "ict_index",
            "selected_by_percent",
        ]
        for col in float_cols:
            if col in df.columns:
                df[col] = df[col].astype("float64")

        # Add team and position info
        teams_info = self._transform_teams()[["team", "team_name_long"]]
        positions_info = self._transform_positions()[["position", "pos_name_long"]]

        df = df.merge(teams_info, on="team_id", how="left")
        df = df.merge(positions_info, on="position_id", how="left")

        # Filter active players only
        if "minutes_played" in df.columns:
            df = df[df["minutes_played"] > 0]

        # Calculate additional stats if in full mode
        if not self.compact and "minutes_played" in df.columns:
            df = self._add_per_90_stats(df)

        return df.set_index("player_id") if "player_id" in df.columns else df

    def _transform_teams(self) -> pd.DataFrame:
        """Transform raw team data into clean DataFrame."""
        essential_cols = {
            "team_id",
            "team",
            "team_name_long",
            "strength",
            "strength_overall_home",
            "strength_overall_away",
        }

        df = pd.DataFrame(self.teams_json)

        # Rename columns
        renames = {"id": "team_id", "short_name": "team", "name": "team_name_long"}
        df = df.rename(columns=renames)

        # Exclude unwanted columns
        exclude_cols = {
            "code",
            "played",
            "form",
            "win",
            "draw",
            "loss",
            "points",
            "position",
            "team_division",
            "unavailable",
            "pulse_id",
        }
        df = df.drop([col for col in exclude_cols if col in df.columns], axis=1)

        # Apply compact mode
        if self.compact:
            available_essential = [col for col in essential_cols if col in df.columns]
            df = df[available_essential]

        return df.set_index("team_id")

    def _transform_positions(self) -> pd.DataFrame:
        """Transform raw position data into clean DataFrame."""
        df = pd.DataFrame(self.element_types_json)

        # Rename columns
        renames = {
            "id": "position_id",
            "singular_name": "pos_name_long",
            "singular_name_short": "position",
            "element_count": "count",
        }
        df = df.rename(columns=renames)

        # Exclude unwanted columns
        exclude_cols = {
            "plural_name",
            "plural_name_short",
            "ui_shirt_specific",
            "sub_positions_locked",
        }
        df = df.drop([col for col in exclude_cols if col in df.columns], axis=1)

        return df.set_index("position_id")

    def _transform_gameweeks(self) -> pd.DataFrame:
        """Transform raw gameweek data into clean DataFrame."""
        df = pd.json_normalize(self.events_json)

        # Exclude unwanted columns
        exclude_cols = {
            "chip_plays",
            "top_element",
            "top_element_info",
            "deadline_time_epoch",
            "deadline_time_game_offset",
            "cup_leagues_created",
            "h2h_ko_matches_created",
        }
        df = df.drop([col for col in exclude_cols if col in df.columns], axis=1)

        # Rename columns
        renames = {
            "id": "GW",
            "average_entry_score": "average_manager_points",
            "highest_scoring_entry": "top_manager_id",
            "highest_score": "top_manager_score",
        }
        df = df.rename(columns=renames)

        return df.set_index("GW")

    def _add_per_90_stats(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add per-90 minute statistics to player DataFrame."""
        per_90_stats = {
            "total_points_per_90": "total_points",
            "goals_scored_per_90": "goals_scored",
            "assists_per_90": "assists",
            "bonus_points_system_per_90": "bonus_points_system",
            "influence_per_90": "influence",
            "creativity_per_90": "creativity",
            "threat_per_90": "threat",
            "ict_index_per_90": "ict_index",
        }

        for new_col, base_col in per_90_stats.items():
            if base_col in df.columns:
                df[new_col] = df[base_col] / df["minutes_played"] * 90

        # Add goal involvements
        if "goals_scored" in df.columns and "assists" in df.columns:
            df["goal_involvements"] = df["goals_scored"] + df["assists"]
            df["goal_involvements_per_90"] = (
                df["goal_involvements"] / df["minutes_played"] * 90
            )

        return df.round(1)

    def get_fixtures_matrix(
        self, start_gw: Optional[int] = None, num_gw: int = 8
    ) -> pd.DataFrame:
        """Get all fixtures in range (start_gw, end_gw)"""

        # if no start gw provided, use next gameweek
        if not start_gw:
            start_gw = self.next_gw

        end_gw = start_gw + num_gw

        team_names = self.teams_df[["team"]]

        # create fixtures dataframe
        fixtures = (
            pd.json_normalize(self.fixtures_json)
            .merge(
                # join to team names (home)
                team_names,
                left_on="team_h",
                right_on="team_id",
                suffixes=[None, "_home"],
            )
            .merge(
                # join to team names (away)
                team_names,
                left_on="team_a",
                right_on="team_id",
                suffixes=[None, "_away"],
            )
            .rename(columns={"id": "fixture_id", "event": "GW", "team": "team_home"})
            .drop(
                [
                    "code",
                    "finished_provisional",
                    "kickoff_time",
                    "minutes",
                    "provisional_start_time",
                    "started",
                    "stats",
                    "pulse_id",
                ],
                axis=1,
            )
        )

        # filter between start_gw and end_gw
        fixtures = fixtures[(fixtures["GW"] >= start_gw) & (fixtures["GW"] <= end_gw)]

        # team ids (index) vs fixture difficulty ratings (columns)
        home_ratings = fixtures.pivot(
            index="team_home", columns="GW", values="team_h_difficulty"
        ).fillna(0)
        away_ratings = fixtures.pivot(
            index="team_away", columns="GW", values="team_a_difficulty"
        ).fillna(0)

        # team names (index) vs opposition team names (columns)
        home_team_names_pivot = fixtures.pivot(
            index="team_home", columns="GW", values="team_away"
        )
        home_team_names = home_team_names_pivot.apply(
            lambda s: s + " (H)" if s is not None else None  # type: ignore[operator]
        ).fillna("")
        away_team_names_pivot = fixtures.pivot(
            index="team_away", columns="GW", values="team_home"
        )
        away_team_names = away_team_names_pivot.apply(
            lambda s: s + " (A)" if s is not None else None  # type: ignore[operator]
        ).fillna("")

        fx_ratings = home_ratings + away_ratings
        fx_team_names = home_team_names + away_team_names

        # change column names
        col_names = [int(c) for c in fx_team_names.columns]
        fx_ratings.columns, fx_team_names.columns = col_names, col_names

        # combine team names with FDR
        fx = fx_team_names + " " + fx_ratings.astype(int).astype(str)

        # calculate average FDR per team
        # ignore 0s (blank fixtures)
        fx["avg_FDR"] = fx_ratings.replace(0, None).mean(axis=1)

        fx = fx.sort_values("avg_FDR").drop("avg_FDR", axis=1).replace(" 0", "")

        return fx
