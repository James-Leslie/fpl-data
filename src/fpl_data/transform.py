from fpl_data.load import FplApiDataRaw, get_element_summary
import numpy as np
import pandas as pd


RENAME_COLUMNS = {
    'id': 'player_id',
    'team': 'team_id',
    'team_name': 'team',
    'element_type': 'position_id',
    'pos': 'pos',
    'first_name': 'first_name',
    'second_name': 'second_name',
    'web_name': 'player_name',
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
    'I90': 'I90',
    'C90': 'C90',
    'T90': 'T90',
    'II90': 'II90',
    'selected_by_percent': 'TSB%'
}


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
        first_deadline = self.events_json[0]['deadline_time']
        # Extract the year portion from the date string
        year = first_deadline[:4]
        # Calculate the next year
        self.season = f'{year}-{str(int(year) + 1)[-2:]}'

        # Get next gameweek
        self.next_gw = 1  # default, to be updated with actual value
        # search for gameweek with is_next property = true
        for event in self.events_json:
            if event['is_next']:
                self.next_gw = event['id']
                break

        # ----------------------------------------------------------- gameweeks
        gameweeks = pd.json_normalize(
            self.events_json
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
            self.element_types_json
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
            self.teams_json
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
        players = pd.DataFrame(
            self.elements_json
        ).rename(
            # rename columns
            columns=RENAME_COLUMNS
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

        # exclude players who haven't played any minutes
        players = players[players['MP'] > 0]

        # calculate additional per 90 stats
        players = players.assign(
            GI=lambda x: x.GS + x.A,
            Pts90=lambda x: x.Pts / x.MP * 90,
            GS90=lambda x: x.GS / x.MP * 90,
            A90=lambda x: x.A / x.MP * 90,
            GI90=lambda x: (x.GS + x.A) / x.MP * 90,
            BPS90=lambda x: x.BPS / x.MP * 90,
            I90=lambda x: x.I / x.MP * 90,
            C90=lambda x: x.C / x.MP * 90,
            T90=lambda x: x['T'] / x.MP * 90,
            II90=lambda x: x.II / x.MP * 90
        )

        # convert price to in-game values
        players['£'] = players['£'] / 10

        # select only columns of interest
        players = players[
            RENAME_COLUMNS.values()
        ].drop(
            ['team_id', 'position_id'],
            axis=1
        ).set_index(
            'player_id'
        ).round(1)

        self.gameweeks_df = gameweeks
        self.teams_df = teams
        self.positions_df = positions
        self.players_df = players

    def get_fixtures_matrix(self, start_gw=None, num_gw=8):
        '''Get all fixtures in range (start_gw, end_gw)'''

        # if no start gw provided, use next gameweek
        if not start_gw:
            start_gw = self.next_gw

        end_gw = start_gw + num_gw

        team_names = self.teams_df[['team']]

        # create fixtures dataframe
        fixtures = pd.json_normalize(
            self.fixtures_json
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
            index='team_home', columns='GW', values='team_h_difficulty'
        ).fillna(0)
        away_ratings = fixtures.pivot(
            index='team_away', columns='GW', values='team_a_difficulty'
        ).fillna(0)

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
        col_names = [int(c) for c in fx_team_names.columns]
        fx_ratings.columns, fx_team_names.columns = col_names, col_names

        # combine team names with FDR
        fx = fx_team_names + ' ' + fx_ratings.astype(int).astype(str)

        # calculate average FDR per team
        # ignore 0s (blank fixtures)
        fx['avg_FDR'] = fx_ratings.replace(0, None).mean(axis=1)

        fx = fx.sort_values(
            'avg_FDR'
        ).drop(
            'avg_FDR', axis=1
        ).replace(
            ' 0', ''
        )

        return fx

    def get_player_summary(self, player_id, type='history'):

        print('Fetching\n...')
        element_summary = get_element_summary(player_id)
        print('DONE!\n')

        df = pd.json_normalize(
            element_summary[type]
        ).rename(
            # rename columns
            columns=RENAME_COLUMNS
        )

        if type == 'fixtures':
            df['team_id'] = df.apply(
                lambda x: x.team_a if x.is_home else x.team_h,
                axis=1
            )

            df['gw'] = df['event_name'].apply(
                lambda x: str(x).split(' ')[-1]
            )

            # join team names
            df = df.merge(
                self.teams_df[['team']],
                on='team_id'
            ).sort_values(
                'event'
            )[[
                'gw', 'team', 'difficulty'
            ]].set_index(
                'gw'
            )

        if type == 'history':
            df = df.merge(
                # get opponent team names
                self.teams_df['team'],
                left_on='opponent_team',
                right_on='team_id'
            )

            # add opponent column, e.g. BUR (A) or ARS (H)
            df['was_home'] = df['was_home'].astype('bool')
            df = df.assign(
                opponent=lambda x: np.where(
                    x['was_home'],
                    f'{x.team[0]} (H)', f'{x.team[0]} (A)'
                ),
                score=lambda x: f'{x.team_h_score[0]} - {x.team_a_score[0]}',
                value=lambda x: np.round(x.value / 10, 1)
            )

            df = df.rename(columns={
                'value': '£',
                'transfers_balance': 'NT',
                'selected': 'SB'
            })

            # column ordering
            df['gw'] = df['round'].astype(int)
            df = df.sort_values('gw')[[
                'gw', 'opponent', 'score', 'Pts', 'ST', 'MP', 'GS', 'A', 'xG',
                'xA', 'xGI', 'CS', 'GC', 'xGC', 'OG', 'PS', 'PM', 'YC', 'RC',
                'S', 'B', 'BPS', 'I', 'C', 'T', 'II', 'NT', 'SB', '£'
            ]].set_index(
                'gw'
            )

        return df
