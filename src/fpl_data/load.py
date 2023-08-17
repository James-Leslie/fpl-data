import requests
import time
from tqdm.auto import tqdm
from fpl_data.utils import drop_keys


BASE_URL = 'https://fantasy.premierleague.com/api/'


class FplApiDataRaw:

    def __init__(self):
        '''Downloads all relevant data from FPL API, including:
          - elements (players)
          - element_types (positions)
          - teams
          - events (game week dates)
          - fixtures (schedule)'''

        # Bootstrap-static data
        print('Getting data from API\n...')
        data = requests.get(BASE_URL+'bootstrap-static/').json()
        print('DONE!\n')
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
        self.fixtures = fixtures

        # Get current season
        first_deadline = self.events[0]['deadline_time']
        # Extract the year portion from the date string
        year = first_deadline[:4]
        # Calculate the next year
        self.season = f'{year}-{str(int(year) + 1)[-2:]}'

    def get_all_element_summaries(self):
        '''Get summaries for each element'''
        history = []
        history_past = []

        # get all element_ids from self.elements
        element_ids = [e['id'] for e in self.elements]

        # loop through all element_ids and get summaries
        for element_id in tqdm(element_ids):
            summary = get_element_summary(element_id)
            # combine summaries of all elements together
            history += summary['history']
            history_past += summary['history_past']

        # return current and past season summaries together
        all_summaries = {
            'history': history,
            'history_past': history_past
        }
        return all_summaries


def get_element_summary(player_id):
    '''Get all past gameweek/season info for a given player_id,
       wait between requests to avoid API rate limit'''

    success = False
    # try until a result is returned
    while not success:
        try:
            # send GET request to BASE_URL/api/element-summary/{PID}/
            data = requests.get(
                BASE_URL + 'element-summary/' + str(player_id) + '/').json()
            success = True
        except (
            requests.exceptions.RequestException,
            requests.exceptions.HTTPError
        ):
            # Wait a bit to avoid API rate limits, if needed
            time.sleep(.3)

    # history_past needs element id key added
    for d in data['history_past']:
        d['element'] = player_id

    return data
