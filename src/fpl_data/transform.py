from fpl_data.load import FplApiDataRaw
import pandas as pd


class FplApiDataTransformed(FplApiDataRaw):

    def __init__(self):
        '''Transforms data from FPL API and outputs results as dataframes:
          - players
          - positions
          - teams
          - gameweeks
          - fixtures (schedule)'''

        # Download raw data
        super().__init__()

        # Get current season
        first_deadline = self.events[0]['deadline_time']
        # Extract the year portion from the date string
        year = first_deadline[:4]
        # Calculate the next year
        self.season = f'{year}-{str(int(year) + 1)[-2:]}'

        # Get next gameweek
        self.next_gw = 1  # default state

        for event in self.events:
            if event['is_next']:
                self.next_gw = event['id']
                break

        # ----------------------------------------------------------- gameweeks
        gameweeks = pd.json_normalize(
            self.events
        ).drop(
            ['chip_plays', 'top_element', 'top_element_info',
             'deadline_time_epoch', 'deadline_time_game_offset',
             'cup_leagues_created', 'h2h_ko_matches_created'],
            axis=1
        ).rename(columns={
            'id': 'GW',
            'average_entry_score': 'average_manager_points',
            'highest_scoring_entry': 'top_manager_id',
            'highest_score': 'top_manager_score',
            'top_element_info.id': 'top_player_id',
            'top_element_info.points': 'top_player_points'}
        ).set_index(
            'GW'
        )

        # ----------------------------------------------------------- positions
        positions = pd.DataFrame(
            self.element_types
        ).drop(
            ['plural_name', 'plural_name_short', 'ui_shirt_specific',
             'sub_positions_locked'],
            axis=1
        ).rename(columns={
            'id': 'position_id',
            'singular_name': 'pos_name_long',
            'singular_name_short': 'pos',
            'element_count': 'count'}
        ).set_index(
            'position_id'
        )

        # --------------------------------------------------------------- teams
        teams = pd.DataFrame(
            self.teams
        ).drop(
            ['code', 'played', 'form', 'win', 'draw', 'loss', 'points',
             'position', 'team_division', 'unavailable', 'pulse_id'],
            axis=1
        ).rename(columns={
            'id': 'team_id',
            'short_name': 'team',
            'name': 'team_name_long'}
        ).set_index(
            'team_id'
        )

        # ------------------------------------------------------------- players
        rename_columns = {
            'id': 'player_id',
            'team': 'team_id',
            'team_name': 'team',
            'element_type': 'position_id',
            'pos': 'pos',
            'web_name': 'name',
            'now_cost': '£',
            'starts': 'ST',
            'minutes': 'MP',
            'total_points': 'Pts',
            'goals_scored': 'GS',
            'assists': 'A',
            'GI': 'GI',
            'expected_goals': 'xG',
            'expected_assists': 'xA',
            'expected_goal_involvements': 'xGI',
            'points_per_game': 'PPG',
            'Pts90': 'Pts90',
            'GS90': 'GS90',
            'A90': 'A90',
            'GI90': 'GI90',
            'expected_goals_per_90': 'xG90',
            'expected_assists_per_90': 'xA90',
            'expected_goal_involvements_per_90': 'xGI90',
            'clean_sheets': 'CS',
            'goals_conceded': 'GC',
            'expected_goals_conceded': 'xGC',
            'goals_conceded_per_90': 'GC90',
            'expected_goals_conceded_per_90': 'xGC90',
            'own_goals': 'OG',
            'penalties_saved': 'PS',
            'penalties_missed': 'PM',
            'yellow_cards': 'YC',
            'red_cards': 'RC',
            'saves': 'S',
            'saves_per_90': 'S90',
            'bonus': 'B',
            'bps': 'BPS',
            'BPS90': 'BPS90',
            'influence': 'I',
            'creativity': 'C',
            'threat': 'T',
            'ict_index': 'II',
            'II90': 'II90',
            'selected_by_percent': 'TSB%'
        }

        players = pd.DataFrame(
            self.elements
        ).rename(
            # rename columns
            columns=rename_columns
        ).astype({
            # change data types
            'PPG': 'float64',
            'xG': 'float64',
            'xA': 'float64',
            'xGI': 'float64',
            'xGC': 'float64',
            'I': 'float64',
            'C': 'float64',
            'T': 'float64',
            'II': 'float64',
            'TSB%': 'float64'
        }).merge(
            teams[['team', 'team_name_long']], on='team_id'
        ).merge(
            positions[['pos', 'pos_name_long']], on='position_id'
        )

        # exclude who haven't played any minutes
        players = players[players['MP'] > 0]

        # calculate additional per 90 stats
        players = players.assign(
            GI=lambda x: x.GS + x.A,
            Pts90=lambda x: x.Pts / x.MP * 90,
            GS90=lambda x: x.GS / x.MP * 90,
            A90=lambda x: x.A / x.MP * 90,
            GI90=lambda x: (x.GS + x.A) / x.MP * 90,
            BPS90=lambda x: x.BPS / x.MP * 90,
            II90=lambda x: x.II / x.MP * 90,
        )

        # convert price to in-game values
        players['£'] = players['£'] / 10

        # select only columns of interest
        players = players[
            rename_columns.values()
        ].drop(
            ['team_id', 'position_id'],
            axis=1
        ).set_index(
            'player_id'
        ).round(1)

        self.gameweeks = gameweeks
        self.teams = teams
        self.positions = positions
        self.players = players

        # raw data not needed anymore
        del self.elements
        del self.element_types
        del self.events

    def get_fixtures_matrix(self, start_gw=None, num_gw=8):
        '''Get all fixtures in range (start_gw, end_gw)'''

        # if no start gw provided, use next gameweek
        if not start_gw:
            start_gw = self.next_gw

        end_gw = start_gw + num_gw

        team_names = self.teams[['team']]

        # create fixtures dataframe
        fixtures = pd.json_normalize(
            self.fixtures
        ).merge(
            # join to team names (home)
            team_names,
            left_on='team_h',
            right_on='team_id',
            suffixes=[None, '_home']
        ).merge(
            # join to team names (away)
            team_names,
            left_on='team_a',
            right_on='team_id',
            suffixes=[None, '_away']
        ).rename(columns={
            'id': 'fixture_id',
            'event': 'GW',
            'team': 'team_home'}
        ).drop(
            ['code', 'finished_provisional', 'kickoff_time', 'minutes',
             'provisional_start_time', 'started', 'stats', 'pulse_id'],
            axis=1
        )

        # filter between start_gw and end_gw
        fixtures = fixtures[
            (fixtures['GW'] >= start_gw) & (fixtures['GW'] <= end_gw)]

        # team ids (index) vs fixture difficulty ratings (columns)
        home_ratings = fixtures.pivot(
            index='team_h', columns='GW', values='team_h_difficulty').fillna(0)
        away_ratings = fixtures.pivot(
            index='team_a', columns='GW', values='team_a_difficulty').fillna(0)

        # team names (index) vs opposition team names (columns)
        home_team_names = fixtures.pivot(
            index='team_home', columns='GW', values='team_away')
        home_team_names = home_team_names.apply(lambda s: s + ' (H)'
                                                if s is not None
                                                else None).fillna('')
        away_team_names = fixtures.pivot(
            index='team_away', columns='GW', values='team_home')
        away_team_names = away_team_names.apply(lambda s: s + ' (A)'
                                                if s is not None
                                                else None).fillna('')

        fx_ratings = home_ratings + away_ratings
        fx_team_names = home_team_names + away_team_names

        # change column names
        fx_team_names.columns = [int(c) for c in fx_team_names.columns]

        return fx_ratings, fx_team_names
