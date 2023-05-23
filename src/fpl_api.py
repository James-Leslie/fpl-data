import requests
import time
from tqdm.auto import tqdm

BASE_URL = 'https://fantasy.premierleague.com/api/'


def drop_keys(d, keys):
    '''Drop keys from a dictionary'''
    return {k: v for k, v in d.items() if k not in keys}


def get_element_summary(player_id, type):
    '''Get all past season info for a given player_id,
       wait between requests to avoid API rate limit'''

    success = False
    # try until a result is returned
    while not success:
        try:
            # send GET request to BASE_URL/api/element-summary/{PID}/
            data = requests.get(
                BASE_URL + 'element-summary/' + str(player_id) + '/').json()
            success = True
        except:
            # wait a bit to avoid API rate limits, if needed
            time.sleep(.3)

    # extract 'history_past' data from response into dataframe
    df = pd.json_normalize(data[type])

    # season history needs player id column added
    if type == 'history_past':
        df.insert(0, 'id', player_id)

    return df


class FplApiData:

    def __init__(self):
        '''Downloads all relevant data from FPL API, including:
          - elements (players)
          - element_types (positions)
          - teams
          - events (game week dates)
          - fixtures (schedule)'''

        # Bootstrap-static data
        data = requests.get(BASE_URL+'bootstrap-static/').json()
        # delete unnecessary keys
        data = drop_keys(
            data,
            ['element_stats', 'game_settings', 'total_players', 'phases']
        )

        self.elements = data['elements']  # players
        self.element_types = data['element_types']  # positions
        self.teams = data['teams']  # teams
        self.events = data['events']  # game weeks

        # fixture data
        fixtures = requests.get(BASE_URL+'fixtures/').json()
        # drop unnecessary keys
        drop_cols = ['code', 'finished_provisional', 'minutes',
                     'provisional_start_time', 'started', 'stats', 'pulse_id']
        self.fixtures = [drop_keys(f, drop_cols) for f in fixtures]
