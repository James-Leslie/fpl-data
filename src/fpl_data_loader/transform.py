from typing import Optional

import pandas as pd

from fpl_data_loader.load import FplApiDataRaw, get_element_summary

# Column renaming for better readability - using snake_case descriptive names
RENAME_COLUMNS = {
    # Player identification
    "id": "player_id",
    "team": "team_id",
    "element_type": "position_id",
    "pos": "position",
    "first_name": "first_name",
    "second_name": "last_name",
    "web_name": "player_name",
    "now_cost": "price",
    # Match stats
    "starts": "starts",
    "minutes": "minutes_played",
    "total_points": "total_points",
    # Attacking stats
    "goals_scored": "goals_scored",
    "assists": "assists",
    "expected_goals": "expected_goals",
    "expected_assists": "expected_assists",
    "expected_goal_involvements": "expected_goal_involvements",
    "expected_goals_per_90": "expected_goals_per_90",
    "expected_assists_per_90": "expected_assists_per_90",
    "expected_goal_involvements_per_90": "expected_goal_involvements_per_90",
    # Defensive stats
    "clean_sheets": "clean_sheets",
    "goals_conceded": "goals_conceded",
    "expected_goals_conceded": "expected_goals_conceded",
    "goals_conceded_per_90": "goals_conceded_per_90",
    "expected_goals_conceded_per_90": "expected_goals_conceded_per_90",
    "saves": "saves",
    "saves_per_90": "saves_per_90",
    # Disciplinary & miscellaneous
    "own_goals": "own_goals",
    "penalties_saved": "penalties_saved",
    "penalties_missed": "penalties_missed",
    "yellow_cards": "yellow_cards",
    "red_cards": "red_cards",
    # Bonus & ICT stats
    "bonus": "bonus_points",
    "bps": "bonus_points_system",
    "influence": "influence",
    "creativity": "creativity",
    "threat": "threat",
    "ict_index": "ict_index",
    # Other stats
    "points_per_game": "points_per_game",
    "selected_by_percent": "selected_by_percent",
}


class FplApiDataTransformed(FplApiDataRaw):
    def __init__(self) -> None:
        """Transforms data from FPL API and outputs results as dataframes:
        - players
        - positions
        - teams
        - gameweeks
        - fixtures (schedule)"""

        # Download raw data
        super().__init__()

        # Get current season
        first_deadline = self.events_json[0]["deadline_time"]
        # Extract the year portion from the date string
        year = first_deadline[:4]
        # Calculate the next year
        self.season = f"{year}-{str(int(year) + 1)[-2:]}"

        # Get next gameweek
        self.next_gw = 1  # default, to be updated with actual value
        # search for gameweek with is_next property = true
        for event in self.events_json:
            if event["is_next"]:
                self.next_gw = event["id"]
                break

        # ----------------------------------------------------------- gameweeks
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
                    "id": "GW",
                    "average_entry_score": "average_manager_points",
                    "highest_scoring_entry": "top_manager_id",
                    "highest_score": "top_manager_score",
                    "top_element_info.id": "top_player_id",
                    "top_element_info.points": "top_player_points",
                }
            )
            .set_index("GW")
        )

        # ----------------------------------------------------------- positions
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
                    "singular_name": "pos_name_long",
                    "singular_name_short": "position",
                    "element_count": "count",
                }
            )
            .set_index("position_id")
        )

        # --------------------------------------------------------------- teams
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

        # ------------------------------------------------------------- players
        players = (
            pd.DataFrame(self.elements_json)
            .rename(
                # rename columns
                columns=RENAME_COLUMNS
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
            .merge(teams[["team", "team_name_long"]], on="team_id")
            .merge(positions[["position", "pos_name_long"]], on="position_id")
        )

        # exclude players who haven't played any minutes
        players = players[players["minutes_played"] > 0]

        # calculate additional per 90 stats
        players = players.assign(
            goal_involvements=lambda x: x.goals_scored + x.assists,
            total_points_per_90=lambda x: x.total_points / x.minutes_played * 90,
            goals_scored_per_90=lambda x: x.goals_scored / x.minutes_played * 90,
            assists_per_90=lambda x: x.assists / x.minutes_played * 90,
            goal_involvements_per_90=lambda x: (x.goals_scored + x.assists)
            / x.minutes_played
            * 90,
            bonus_points_system_per_90=lambda x: x.bonus_points_system
            / x.minutes_played
            * 90,
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

        self.gameweeks_df = gameweeks
        self.teams_df = teams
        self.positions_df = positions
        self.players_df = players

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

        df = pd.json_normalize(element_summary[type]).rename(
            # rename columns
            columns=RENAME_COLUMNS
        )

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
