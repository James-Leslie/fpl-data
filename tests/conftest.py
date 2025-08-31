import json
from pathlib import Path
from typing import Dict, Any, List

import pytest


@pytest.fixture
def sample_players() -> List[Dict[str, Any]]:
    """Load sample player data for testing."""
    fixtures_dir = Path(__file__).parent / "fixtures"
    with open(fixtures_dir / "sample_players.json") as f:
        return json.load(f)


@pytest.fixture
def sample_teams() -> List[Dict[str, Any]]:
    """Load sample team data for testing."""
    fixtures_dir = Path(__file__).parent / "fixtures"
    with open(fixtures_dir / "sample_teams.json") as f:
        return json.load(f)


@pytest.fixture
def sample_positions() -> List[Dict[str, Any]]:
    """Sample position data for testing."""
    return [
        {"id": 1, "singular_name": "Goalkeeper", "singular_name_short": "GKP"},
        {"id": 2, "singular_name": "Defender", "singular_name_short": "DEF"},
        {"id": 3, "singular_name": "Midfielder", "singular_name_short": "MID"},
        {"id": 4, "singular_name": "Forward", "singular_name_short": "FWD"},
    ]
