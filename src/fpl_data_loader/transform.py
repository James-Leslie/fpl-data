from typing import Optional

import pandas as pd

from fpl_data_loader.load import FplDataLoader, get_element_summary


class FplDataTransformer(FplDataLoader):
    """Transforms data from FPL API and outputs results as dataframes:

    Transforms raw FPL API data into clean pandas DataFrames with user-friendly
    column names. Supports both compact mode (essential columns) and full mode
    (all useful columns) for different use cases.
    """

    def __init__(self) -> None:
        """Initialize transformer and create clean DataFrames.

        Args:
            compact (bool): If True, return only essential columns for fantasy analysis.
                          If False, return all useful columns for detailed analysis.
        """

        # Download raw data
        super().__init__()

        # Calculate current season and next gameweek
        self.season = self._get_current_season()
        self.next_gw = self._get_next_gameweek()

        # Transform all data types
        self.gameweeks_df = self._transform_gameweeks()
        self.teams_df = self._transform_teams()
        self.positions_df = self._transform_positions()
        self.players_df = self._transform_players()

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

    def _transform_gameweeks(self) -> pd.DataFrame:
        """Transform gameweeks data into a clean DataFrame."""
        gameweeks = (
            pd.json_normalize(self.events_json)
            .drop(
                [
                    "chip_plays",
                    "top_element",
                    "top_element_info",
                    "deadline_time_epoch",
                    "deadline_time_game_offset",
                    "cup_leagues_created",
                    "h2h_ko_matches_created",
                ],
                axis=1,
            )
            .rename(
                columns={
                    "id": "gameweek",
                    "average_entry_score": "average_manager_points",
                    "highest_scoring_entry": "top_manager_id",
                    "highest_score": "top_manager_score",
                    "top_element_info.id": "top_player_id",
                    "top_element_info.points": "top_player_points",
                }
            )
            .set_index("gameweek")
        )

        return gameweeks

    def _transform_teams(self) -> pd.DataFrame:
        """Transform teams data into a clean DataFrame."""
        teams = (
            pd.DataFrame(self.teams_json)
            .drop(
                [
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
                ],
                axis=1,
            )
            .rename(
                columns={
                    "id": "team_id",
                    "short_name": "team",
                    "name": "team_name_long",
                }
            )
            .set_index("team_id")
        )

        return teams

    def _transform_positions(self) -> pd.DataFrame:
        """Transform positions data into a clean DataFrame."""
        positions = (
            pd.DataFrame(self.element_types_json)
            .drop(
                [
                    "plural_name",
                    "plural_name_short",
                    "ui_shirt_specific",
                    "sub_positions_locked",
                ],
                axis=1,
            )
            .rename(
                columns={
                    "id": "position_id",
                    "singular_name": "position_name_long",
                    "singular_name_short": "position",
                    "element_count": "count",
                }
            )
            .set_index("position_id")
        )

        return positions

    def _calculate_expected_points(self, df: pd.DataFrame) -> pd.Series:
        """Calculate expected FPL points based on underlying stats and position.

        Args:
            df: DataFrame with player data including position_id and expected stats

        Returns:
            Series of expected points per player
        """
        # Position-specific goal points
        goal_points = df.position_id.map({1: 6, 2: 6, 3: 5, 4: 4})  # GKP/DEF/MID/FWD

        # Calculate components
        expected_goal_points = df.expected_goals * goal_points
        expected_assist_points = df.expected_assists * 3

        # Clean sheet probability and points (only if 60+ minutes)
        clean_sheet_prob = 1 / (1 + df.expected_goals_conceded)
        clean_sheet_points = df.position_id.map({1: 4, 2: 4, 3: 1, 4: 0})
        minutes_60_plus = (df.minutes_played >= 60).astype(int)
        expected_clean_sheet_points = (
            clean_sheet_prob * clean_sheet_points * minutes_60_plus
        )

        # Minutes points: 1pt for playing, +1pt for 60+ minutes
        minutes_points = (df.minutes_played > 0).astype(int) + (
            df.minutes_played >= 60
        ).astype(int)

        return (
            expected_goal_points
            + expected_assist_points
            + expected_clean_sheet_points
            + minutes_points
        )

    def _transform_players(self) -> pd.DataFrame:
        """Transform players data into a clean DataFrame."""

        players = (
            pd.DataFrame(self.elements_json)
            # Exclude players who haven't played any minutes and can_select is True
            .query("minutes > 0 and can_select")
            # Rename columns for clarity
            .rename(
                columns={
                    "id": "player_id",
                    "team": "team_id",
                    "element_type": "position_id",
                    "second_name": "last_name",
                    "web_name": "short_name",
                    "now_cost": "price",
                    "minutes": "minutes_played",
                }
            )
            # Drop columns that are not needed
            .drop(
                columns=[
                    "can_transact",
                    "can_select",
                    "code",
                    "photo",
                    "removed",
                    "squad_number",
                    "status",
                    "team_code",
                    "region",
                    "team_join_date",
                    "birth_date",
                    "has_temporary_code",
                    "opta_code",
                ]
            )
            .astype(
                {
                    # change data types
                    "points_per_game": "float64",
                    "expected_goals": "float64",
                    "expected_assists": "float64",
                    "expected_goal_involvements": "float64",
                    "expected_goals_conceded": "float64",
                    "influence": "float64",
                    "creativity": "float64",
                    "threat": "float64",
                    "ict_index": "float64",
                    "selected_by_percent": "float64",
                }
            )
            # Merge with teams and positions data
            .merge(self.teams_df[["team", "team_name_long"]], on="team_id")
            .merge(
                self.positions_df[["position", "position_name_long"]], on="position_id"
            )
        )

        # Add expected points using dedicated calculation method
        players["expected_points"] = self._calculate_expected_points(players)

        # calculate additional per 90 stats
        players = players.assign(
            goal_involvements=lambda x: x.goals_scored + x.assists,
            total_points_per_90=lambda x: x.total_points / x.minutes_played * 90,
            goals_scored_per_90=lambda x: x.goals_scored / x.minutes_played * 90,
            assists_per_90=lambda x: x.assists / x.minutes_played * 90,
            goal_involvements_per_90=lambda x: (x.goals_scored + x.assists)
            / x.minutes_played
            * 90,
            expected_points_per_90=lambda x: x.expected_points / x.minutes_played * 90,
            bps_per_90=lambda x: x.bps / x.minutes_played * 90,
            influence_per_90=lambda x: x.influence / x.minutes_played * 90,
            creativity_per_90=lambda x: x.creativity / x.minutes_played * 90,
            threat_per_90=lambda x: x.threat / x.minutes_played * 90,
            ict_index_per_90=lambda x: x.ict_index / x.minutes_played * 90,
        )

        # convert price to in-game values
        players["price"] = players["price"] / 10

        # select only columns of interest
        players = (
            players.drop(["team_id", "position_id"], axis=1)
            .set_index("player_id")
            .round(1)
        )

        return players

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

    def get_player_summary(self, player_id: int, type: str = "history") -> pd.DataFrame:
        print("Fetching\n...")
        element_summary = get_element_summary(player_id)
        print("DONE!\n")

        df = pd.json_normalize(element_summary[type])

        if type == "fixtures":
            df["team_id"] = df.apply(
                lambda x: x.team_a if x.is_home else x.team_h, axis=1
            )

            df["gw"] = df["event_name"].apply(lambda x: str(x).split(" ")[-1])

            # join team names
            df = (
                df.merge(self.teams_df[["team"]], on="team_id")
                .sort_values("event")[["gw", "team", "difficulty"]]
                .set_index("gw")
            )

        if type == "history":
            df = df.merge(
                # get opponent team names
                self.teams_df["team"],
                left_on="opponent_team",
                right_on="team_id",
            )

            # add opponent column, e.g. BUR (A) or ARS (H)
            df["was_home"] = df["was_home"].astype("bool")
            df["opponent"] = df.apply(
                lambda row: row.team + " (H)" if row.was_home else row.team + " (A)",
                axis=1,
            )
            df["score"] = df.apply(
                lambda row: f"{row.team_h_score} - {row.team_a_score}", axis=1
            )
            df["value"] = df["value"] / 10

            df = df.rename(
                columns={
                    "value": "price",
                    "transfers_balance": "net_transfers",
                    "selected": "selected_by",
                }
            )

            # column ordering
            df["gw"] = df["round"].astype(int)
            df = (
                df.sort_values("gw")[
                    [
                        "gw",
                        "opponent",
                        "score",
                        "total_points",
                        "starts",
                        "minutes",
                        "goals_scored",
                        "assists",
                        "expected_goals",
                        "expected_assists",
                        "expected_goal_involvements",
                        "clean_sheets",
                        "goals_conceded",
                        "expected_goals_conceded",
                        "own_goals",
                        "penalties_saved",
                        "penalties_missed",
                        "yellow_cards",
                        "red_cards",
                        "saves",
                        "bonus",
                        "bps",
                        "influence",
                        "creativity",
                        "threat",
                        "ict_index",
                        "net_transfers",
                        "selected_by",
                        "price",
                    ]
                ]
                # change data types
                .astype(
                    {
                        "expected_goals": "float64",
                        "expected_assists": "float64",
                        "expected_goal_involvements": "float64",
                        "expected_goals_conceded": "float64",
                        "influence": "float64",
                        "creativity": "float64",
                        "threat": "float64",
                        "ict_index": "float64",
                    }
                )
                .set_index("gw")
            )

        return df
