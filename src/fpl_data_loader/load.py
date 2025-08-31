import time
from typing import Any, Dict, List

import requests
from requests.exceptions import HTTPError, RequestException
from tqdm.auto import tqdm

from fpl_data_loader.utils import drop_keys

BASE_URL = "https://fantasy.premierleague.com/api/"


class FplApiDataRaw:
    """Raw data loader for Fantasy Premier League API.

    This class fetches and stores raw data from the FPL API endpoints,
    including player information, team data, fixtures, and gameweek events.
    The data is stored in JSON format for further processing and transformation.
    """

    def __init__(self) -> None:
        """Initialize the FPL API data loader and fetch all core data.

        Fetches data from multiple FPL API endpoints:
        - bootstrap-static: Core game data (players, teams, positions, events)
        - fixtures: Match schedule and results

        The constructor automatically removes unnecessary data fields to reduce
        memory usage and focuses on the most relevant data for analysis.

        Raises:
            requests.exceptions.RequestException: If API requests fail.
            requests.exceptions.HTTPError: If HTTP errors occur during data fetch.
        """

        print("Getting data from API\n...")
        data = requests.get(BASE_URL + "bootstrap-static/").json()
        print("DONE!\n")

        # Remove unnecessary data fields to reduce memory usage
        data = drop_keys(
            data, ["element_stats", "game_settings", "total_players", "phases"]
        )

        self.elements_json = data["elements"]
        self.element_types_json = data["element_types"]
        self.teams_json = data["teams"]
        self.events_json = data["events"]

        # Fetch fixture data from separate endpoint
        fixtures = requests.get(BASE_URL + "fixtures/").json()
        self.fixtures_json = fixtures

    def get_all_element_summaries(self) -> Dict[str, List[Dict[str, Any]]]:
        """Fetch detailed performance history for all players.

        Retrieves historical performance data for every player in the current
        season, including both current season gameweek-by-gameweek statistics
        and previous season summary statistics.

        Returns:
            Dict[str, List[Dict[str, Any]]]: Dictionary containing:
                - 'history': List of current season gameweek performances for all players
                - 'history_past': List of previous season summaries for all players

        Note:
            This operation can take several minutes as it makes individual API
            requests for each player. Progress is shown via a progress bar.
        """
        history = []
        history_past = []

        element_ids = [e["id"] for e in self.elements_json]
        for element_id in tqdm(element_ids):
            summary = get_element_summary(element_id)
            # combine summaries of all elements together
            history += summary["history"]
            history_past += summary["history_past"]

        # return current and past season summaries together
        all_summaries = {"history": history, "history_past": history_past}
        return all_summaries


def get_element_summary(player_id: int) -> Dict[str, Any]:
    """Fetch detailed performance history for a specific player.

    Retrieves comprehensive historical data for a player from the FPL API,
    including current season gameweek performances and previous season summaries.
    Implements retry logic with rate limiting to handle API restrictions gracefully.

    Args:
        player_id (int): The unique identifier for the player in the FPL system.

    Returns:
        Dict[str, Any]: Player summary data containing:
            - 'history': List of current season gameweek performances
            - 'history_past': List of previous season summary statistics
            - 'fixtures': Upcoming fixture information for the player

    Raises:
        requests.exceptions.RequestException: If network-related errors occur.
        requests.exceptions.HTTPError: If HTTP errors occur during API requests.

    Note:
        This function includes automatic retry logic with 0.3 second delays
        to respect FPL API rate limits. The function will continue retrying
        until successful data retrieval.
    """
    success = False
    while not success:
        try:
            data = requests.get(
                BASE_URL + "element-summary/" + str(player_id) + "/"
            ).json()
            success = True
        except (RequestException, HTTPError):
            time.sleep(0.3)

    # Add player ID to previous season data for consistent referencing
    for d in data["history_past"]:
        d["element"] = player_id

    return data
