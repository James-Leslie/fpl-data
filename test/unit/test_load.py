import jsonschema
from fpl_data.load import FplApiDataRaw, get_element_summary


# make a request to the FPL API
api_data = FplApiDataRaw()


def test_elements_schema():
    data = api_data.elements_json

    # Define the expected schema for the elements property
    expected_elements_schema = {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "chance_of_playing_next_round": {"type": ["integer", "null"]},
                "chance_of_playing_this_round": {"type": ["integer", "null"]},
                "code": {"type": "integer"},
                "cost_change_event": {"type": "integer"},
                "cost_change_event_fall": {"type": "integer"},
                "cost_change_start": {"type": "integer"},
                "cost_change_start_fall": {"type": "integer"},
                "dreamteam_count": {"type": "integer"},
                "element_type": {"type": "integer"},
                "ep_next": {"type": ["string", "null"]},
                "ep_this": {"type": ["string", "null"]},
                "event_points": {"type": "integer"},
                "first_name": {"type": "string"},
                "form": {"type": "string"},
                "id": {"type": "integer"},
                "in_dreamteam": {"type": "boolean"},
                "news": {"type": "string"},
                "news_added": {
                    "type": ["string", "null"], "format": "date-time"},
                "now_cost": {"type": "integer"},
                "photo": {"type": "string"},
                "points_per_game": {"type": "string"},
                "second_name": {"type": "string"},
                "selected_by_percent": {"type": "string"},
                "special": {"type": "boolean"},
                "squad_number": {"type": ["integer", "null"]},
                "status": {"type": "string"},
                "team": {"type": "integer"},
                "team_code": {"type": "integer"},
                "total_points": {"type": "integer"},
                "transfers_in": {"type": "integer"},
                "transfers_in_event": {"type": "integer"},
                "transfers_out": {"type": "integer"},
                "transfers_out_event": {"type": "integer"},
                "value_form": {"type": "string"},
                "value_season": {"type": "string"},
                "web_name": {"type": "string"},
                "minutes": {"type": "integer"},
                "goals_scored": {"type": "integer"},
                "assists": {"type": "integer"},
                "clean_sheets": {"type": "integer"},
                "goals_conceded": {"type": "integer"},
                "own_goals": {"type": "integer"},
                "penalties_saved": {"type": "integer"},
                "penalties_missed": {"type": "integer"},
                "yellow_cards": {"type": "integer"},
                "red_cards": {"type": "integer"},
                "saves": {"type": "integer"},
                "bonus": {"type": "integer"},
                "bps": {"type": "integer"},
                "influence": {"type": "string"},
                "creativity": {"type": "string"},
                "threat": {"type": "string"},
                "ict_index": {"type": "string"},
                "starts": {"type": "integer"},
                "expected_goals": {"type": "string"},
                "expected_assists": {"type": "string"},
                "expected_goal_involvements": {"type": "string"},
                "expected_goals_conceded": {"type": "string"},
                "influence_rank": {"type": "integer"},
                "influence_rank_type": {"type": "integer"},
                "creativity_rank": {"type": "integer"},
                "creativity_rank_type": {"type": "integer"},
                "threat_rank": {"type": "integer"},
                "threat_rank_type": {"type": "integer"},
                "ict_index_rank": {"type": "integer"},
                "ict_index_rank_type": {"type": "integer"},
                "corners_and_indirect_freekicks_order": {
                    "type": ["integer", "null"]},
                "corners_and_indirect_freekicks_text": {"type": "string"},
                "direct_freekicks_order": {"type": ["integer", "null"]},
                "direct_freekicks_text": {"type": "string"},
                "penalties_order": {"type": ["integer", "null"]},
                "penalties_text": {"type": "string"},
                "expected_goals_per_90": {"type": "number"},
                "saves_per_90": {"type": "number"},
                "expected_assists_per_90": {"type": "number"},
                "expected_goal_involvements_per_90": {"type": "number"},
                "expected_goals_conceded_per_90": {"type": "number"},
                "goals_conceded_per_90": {"type": "number"},
                "now_cost_rank": {"type": "integer"},
                "now_cost_rank_type": {"type": "integer"},
                "form_rank": {"type": "integer"},
                "form_rank_type": {"type": "integer"},
                "points_per_game_rank": {"type": "integer"},
                "points_per_game_rank_type": {"type": "integer"},
                "selected_rank": {"type": "integer"},
                "selected_rank_type": {"type": "integer"},
                "starts_per_90": {"type": "number"},
                "clean_sheets_per_90": {"type": "number"}
            },
            "additionalProperties": False
        }
    }

    # Validate the elements property against the expected schema
    try:
        jsonschema.validate(data, expected_elements_schema)
    except jsonschema.exceptions.ValidationError as e:
        assert False, f"Schema validation failed: {e}"

    assert True


def test_element_types_schema():
    data = api_data.element_types_json

    # Define the expected schema for the element_types property
    expected_element_types_schema = {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "plural_name": {"type": "string"},
                "plural_name_short": {"type": "string"},
                "singular_name": {"type": "string"},
                "singular_name_short": {"type": "string"},
                "squad_select": {"type": "integer"},
                "squad_min_select": {"type": ["integer", "null"]},
                "squad_max_select": {"type": ["integer", "null"]},
                "squad_min_play": {"type": "integer"},
                "squad_max_play": {"type": "integer"},
                "ui_shirt_specific": {"type": "boolean"},
                "sub_positions_locked": {
                    "type": "array",
                    "items": {"type": "integer"}
                },
                "element_count": {"type": "integer"}
            },
            "additionalProperties": False
        },
        "minItems": 4,
        "maxItems": 4
    }

    # Validate the element_types property against the expected schema
    try:
        jsonschema.validate(data, expected_element_types_schema)
    except jsonschema.exceptions.ValidationError as e:
        assert False, f"Schema validation failed: {e}"

    assert True


def test_events_schema():
    data = api_data.events_json

    # Define the expected schema for the events property
    expected_events_schema = {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "name": {"type": "string"},
                "deadline_time": {"type": "string", "format": "date-time"},
                "release_time": {
                    "type": ["string", "null"],
                    "format": "date-time"
                },
                "average_entry_score": {"type": "integer"},
                "finished": {"type": "boolean"},
                "data_checked": {"type": "boolean"},
                "highest_scoring_entry": {"type": ["integer", "null"]},
                "deadline_time_epoch": {"type": "integer"},
                "deadline_time_game_offset": {"type": "integer"},
                "highest_score": {"type": ["integer", "null"]},
                "is_previous": {"type": "boolean"},
                "is_current": {"type": "boolean"},
                "is_next": {"type": "boolean"},
                "cup_leagues_created": {"type": "boolean"},
                "h2h_ko_matches_created": {"type": "boolean"},
                "ranked_count": {"type": "integer"},
                "chip_plays": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "chip_name": {"type": "string"},
                            "num_played": {"type": "integer"}
                        },
                        "additionalProperties": False
                    }
                },
                "most_selected": {"type": ["integer", "null"]},
                "most_transferred_in": {"type": ["integer", "null"]},
                "top_element": {"type": ["integer", "null"]},
                "top_element_info": {
                    "type": ["object", "null"],
                    "properties": {
                        "id": {"type": "integer"},
                        "points": {"type": "integer"}
                    },
                    "additionalProperties": False
                },
                "transfers_made": {"type": "integer"},
                "most_captained": {"type": ["integer", "null"]},
                "most_vice_captained": {"type": ["integer", "null"]}
            },
            "additionalProperties": False
        }
    }

    # Validate the events property against the expected schema
    try:
        jsonschema.validate(data, expected_events_schema)
    except jsonschema.exceptions.ValidationError as e:
        assert False, f"Schema validation failed: {e}"

    assert True


def test_teams_schema():
    data = api_data.teams_json

    # Define the expected schema for the teams property
    expected_teams_schema = {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "code": {"type": "integer"},
                "draw": {"type": "integer"},
                "form": {"type": ["string", "null"]},
                "id": {"type": "integer"},
                "loss": {"type": "integer"},
                "name": {"type": "string"},
                "played": {"type": "integer"},
                "points": {"type": "integer"},
                "position": {"type": "integer"},
                "short_name": {"type": "string"},
                "strength": {"type": "integer"},
                "team_division": {"type": ["string", "null"]},
                "unavailable": {"type": "boolean"},
                "win": {"type": "integer"},
                "strength_overall_home": {"type": "integer"},
                "strength_overall_away": {"type": "integer"},
                "strength_attack_home": {"type": "integer"},
                "strength_attack_away": {"type": "integer"},
                "strength_defence_home": {"type": "integer"},
                "strength_defence_away": {"type": "integer"},
                "pulse_id": {"type": "integer"}
            },
            "additionalProperties": False
        },
        "minItems": 20,
        "maxItems": 20
    }

    # Validate the teams property against the expected schema
    try:
        jsonschema.validate(data, expected_teams_schema)
    except jsonschema.exceptions.ValidationError as e:
        assert False, f"Schema validation failed: {e}"

    assert True


def test_fixtures_schema():
    data = api_data.fixtures_json

    # Define the expected schema for the fixtures property
    expected_fixtures_schema = {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "code": {"type": "integer"},
                "event": {"type": ["integer", "null"]},
                "finished": {"type": "boolean"},
                "finished_provisional": {"type": "boolean"},
                "id": {"type": "integer"},
                "kickoff_time": {"type": ["string", "null"]},
                "minutes": {"type": "integer"},
                "provisional_start_time": {"type": "boolean"},
                "started": {"type": ["boolean", "null"]},
                "team_a": {"type": "integer"},
                "team_a_score": {"type": ["integer", "null"]},
                "team_h": {"type": "integer"},
                "team_h_score": {"type": ["integer", "null"]},
                "stats": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "identifier": {"type": "string"},
                            "a": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "value": {"type": "integer"},
                                        "element": {"type": "integer"}
                                    },
                                    "required": ["value", "element"],
                                    "additionalProperties": False
                                }
                            },
                            "h": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "value": {"type": "integer"},
                                        "element": {"type": "integer"}
                                    },
                                    "required": ["value", "element"],
                                    "additionalProperties": False
                                }
                            }
                        },
                        "required": ["identifier", "a", "h"],
                        "additionalProperties": False
                    }
                },
                "team_h_difficulty": {"type": "integer"},
                "team_a_difficulty": {"type": "integer"},
                "pulse_id": {"type": "integer"}
            },
            "additionalProperties": False
        }
    }

    # Validate the fixtures property against the expected schema
    try:
        jsonschema.validate(data, expected_fixtures_schema)
    except jsonschema.exceptions.ValidationError as e:
        assert False, f"Schema validation failed: {e}"

    assert True


def test_element_summary_schema():
    # Define the expected schema for element summary data
    expected_schema = {
        "type": "object",
        "properties": {
            "fixtures": {"type": "array"},
            "history": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "element": {"type": "integer"},
                        "fixture": {"type": "integer"},
                        "opponent_team": {"type": "integer"},
                        "total_points": {"type": "integer"},
                        "was_home": {"type": "boolean"},
                        "kickoff_time": {"type": "string"},
                        "team_h_score": {"type": "integer"},
                        "team_a_score": {"type": "integer"},
                        "round": {"type": "integer"},
                        "minutes": {"type": "integer"},
                        "goals_scored": {"type": "integer"},
                        "assists": {"type": "integer"},
                        "clean_sheets": {"type": "integer"},
                        "goals_conceded": {"type": "integer"},
                        "own_goals": {"type": "integer"},
                        "penalties_saved": {"type": "integer"},
                        "penalties_missed": {"type": "integer"},
                        "yellow_cards": {"type": "integer"},
                        "red_cards": {"type": "integer"},
                        "saves": {"type": "integer"},
                        "bonus": {"type": "integer"},
                        "bps": {"type": "integer"},
                        "influence": {"type": "string"},
                        "creativity": {"type": "string"},
                        "threat": {"type": "string"},
                        "ict_index": {"type": "string"},
                        "starts": {"type": "integer"},
                        "expected_goals": {"type": "string"},
                        "expected_assists": {"type": "string"},
                        "expected_goal_involvements": {"type": "string"},
                        "expected_goals_conceded": {"type": "string"},
                        "value": {"type": "integer"},
                        "transfers_balance": {"type": "integer"},
                        "selected": {"type": "integer"},
                        "transfers_in": {"type": "integer"},
                        "transfers_out": {"type": "integer"}
                    },
                    "additionalProperties": False
                }
            },
            "history_past": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "season_name": {"type": "string"},
                        "element": {"type": "integer"},
                        "element_code": {"type": "integer"},
                        "start_cost": {"type": "integer"},
                        "end_cost": {"type": "integer"},
                        "total_points": {"type": "integer"},
                        "minutes": {"type": "integer"},
                        "goals_scored": {"type": "integer"},
                        "assists": {"type": "integer"},
                        "clean_sheets": {"type": "integer"},
                        "goals_conceded": {"type": "integer"},
                        "own_goals": {"type": "integer"},
                        "penalties_saved": {"type": "integer"},
                        "penalties_missed": {"type": "integer"},
                        "yellow_cards": {"type": "integer"},
                        "red_cards": {"type": "integer"},
                        "saves": {"type": "integer"},
                        "bonus": {"type": "integer"},
                        "bps": {"type": "integer"},
                        "influence": {"type": "string"},
                        "creativity": {"type": "string"},
                        "threat": {"type": "string"},
                        "ict_index": {"type": "string"},
                        "starts": {"type": "integer"},
                        "expected_goals": {"type": "string"},
                        "expected_assists": {"type": "string"},
                        "expected_goal_involvements": {"type": "string"},
                        "expected_goals_conceded": {"type": "string"}
                    },
                    "additionalProperties": False
                }
            }
        },
        "additionalProperties": False
    }

    # get "history_past" data for player_id=3
    data = get_element_summary(3)

    # Validate the returned data against the expected schema
    try:
        jsonschema.validate(data, expected_schema)
    except jsonschema.exceptions.ValidationError as e:
        assert False, f"Schema validation failed for 'element_summary': {e}"

    assert True
