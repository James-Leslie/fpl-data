from typing import Optional

import pandas as pd

from fpl_data_loader.load import FplApiDataRaw, get_element_summary


class FplDataTransformer(FplApiDataRaw):
    """Data transformer for FPL API data.

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

        # Initialize base class - download raw data from FPL API
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

        renames = {
            "id": "player_id",
            "team": "team_id",
            "element_type": "position_id",
            "second_name": "last_name",
            "web_name": "player_name",
            "now_cost": "price",
            "minutes": "minutes_played",
            "bonus": "bonus_points",
            "bps": "bonus_points_system",
        }
        df = pd.json_normalize(element_summary[type]).rename(columns=renames)

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
                        "minutes_played",
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
                        "bonus_points",
                        "bonus_points_system",
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
