from typing import List, Optional

from pydantic import BaseModel, Field, ValidationError

from fpl_data_loader.load import FplApiDataRaw


class Element(BaseModel):
    """Pydantic model for FPL API element data (players)"""

    model_config = {"extra": "forbid"}

    # Core identifiers
    id: int
    code: int
    web_name: str
    first_name: str
    second_name: str

    # Team and position
    team: int
    team_code: int
    element_type: int

    # Pricing and transfers
    now_cost: int = Field(description="Player cost in FPL currency (£4.5m = 45)")
    cost_change_event: int
    cost_change_event_fall: int
    cost_change_start: int
    cost_change_start_fall: int
    transfers_in: int
    transfers_in_event: int
    transfers_out: int
    transfers_out_event: int

    # Performance stats
    total_points: int  # Can be negative (own goals, red cards, etc.)
    event_points: int
    points_per_game: str  # FPL returns as string
    form: str
    minutes: int = Field(ge=0)
    starts: int = Field(ge=0)

    # Goal/assist stats
    goals_scored: int = Field(ge=0)
    assists: int = Field(ge=0)

    # Defensive stats
    clean_sheets: int = Field(ge=0)
    goals_conceded: int = Field(ge=0)
    own_goals: int = Field(ge=0)

    # Goalkeeper stats
    penalties_saved: int = Field(ge=0)
    saves: int = Field(ge=0)
    saves_per_90: float = Field(ge=0.0)

    # Disciplinary
    yellow_cards: int = Field(ge=0)
    red_cards: int = Field(ge=0)
    penalties_missed: int = Field(ge=0)

    # Bonus and influence
    bonus: int = Field(ge=0)
    bps: int  # BPS can be negative
    influence: str  # FPL returns as string
    creativity: str
    threat: str
    ict_index: str

    # Expected stats (all strings from API)
    expected_goals: str
    expected_assists: str
    expected_goal_involvements: str
    expected_goals_conceded: str
    expected_goals_per_90: float
    expected_assists_per_90: float
    expected_goal_involvements_per_90: float
    expected_goals_conceded_per_90: float

    # Per-90 stats
    goals_conceded_per_90: float
    clean_sheets_per_90: float
    starts_per_90: float

    # Rankings
    influence_rank: int
    influence_rank_type: int
    creativity_rank: int
    creativity_rank_type: int
    threat_rank: int
    threat_rank_type: int
    ict_index_rank: int
    ict_index_rank_type: int
    now_cost_rank: int
    now_cost_rank_type: int
    form_rank: int
    form_rank_type: int
    points_per_game_rank: int
    points_per_game_rank_type: int
    selected_rank: int
    selected_rank_type: int

    # Selection and popularity
    selected_by_percent: str  # FPL returns as string
    dreamteam_count: int = Field(ge=0)
    in_dreamteam: bool

    # Status and availability
    status: str
    news: str
    special: bool
    chance_of_playing_next_round: Optional[int] = Field(None, ge=0, le=100)
    chance_of_playing_this_round: Optional[int] = Field(None, ge=0, le=100)
    squad_number: Optional[int] = None

    # Expected points
    ep_next: Optional[str] = None
    ep_this: Optional[str] = None

    # Metadata
    photo: str
    value_form: str
    value_season: str
    news_added: Optional[str] = None  # ISO datetime string

    # Set pieces
    corners_and_indirect_freekicks_order: Optional[int] = None
    corners_and_indirect_freekicks_text: str
    direct_freekicks_order: Optional[int] = None
    direct_freekicks_text: str
    penalties_order: Optional[int] = None
    penalties_text: str

    # New fields (discovered during schema updates)
    birth_date: Optional[str] = None
    can_select: bool
    can_transact: bool
    clearances_blocks_interceptions: int = Field(ge=0)
    defensive_contribution: int = Field(ge=0)
    defensive_contribution_per_90: float = Field(ge=0.0)
    has_temporary_code: bool
    opta_code: str
    recoveries: int = Field(ge=0)
    region: Optional[int] = None
    removed: bool
    tackles: int = Field(ge=0)
    team_join_date: Optional[str] = None


class ElementType(BaseModel):
    """Pydantic model for FPL API position data (element_types)"""

    id: int
    plural_name: str
    plural_name_short: str
    singular_name: str
    singular_name_short: str
    squad_select: int
    squad_min_select: Optional[int] = None
    squad_max_select: Optional[int] = None
    squad_min_play: int
    squad_max_play: int
    ui_shirt_specific: bool
    sub_positions_locked: List[int]
    element_count: int


class Team(BaseModel):
    """Pydantic model for FPL API team data"""

    id: int
    code: int
    name: str
    short_name: str
    draw: int = Field(ge=0)
    loss: int = Field(ge=0)
    played: int = Field(ge=0)
    points: int = Field(ge=0)
    position: int = Field(ge=1, le=20)
    win: int = Field(ge=0)
    strength: int
    form: Optional[str] = None
    team_division: Optional[str] = None
    unavailable: bool
    strength_overall_home: int
    strength_overall_away: int
    strength_attack_home: int
    strength_attack_away: int
    strength_defence_home: int
    strength_defence_away: int
    pulse_id: int


def test_elements():
    """Test that all current elements validate against Pydantic model"""
    data = FplApiDataRaw()

    try:
        elements = [Element.model_validate(e) for e in data.elements_json]
        print(f"Successfully validated {len(elements)} elements")

        # Basic sanity checks
        assert len(elements) > 700, f"Expected >700 elements, got {len(elements)}"

        # Check we have elements from all positions
        positions = {e.element_type for e in elements}
        assert positions == {1, 2, 3, 4}, f"Missing positions: {positions}"

        # Check we have reasonable cost distribution
        costs = [e.now_cost for e in elements]
        assert min(costs) >= 35, f"Minimum cost too low: {min(costs)}"  # £3.5m
        assert max(costs) <= 150, f"Maximum cost too high: {max(costs)}"  # £15.0m

    except ValidationError as e:
        print("Validation failed with errors:")
        for error in e.errors():
            field = ".".join(str(x) for x in error["loc"])
            print(f"  - {field}: {error['msg']}")
            if "input" in error:
                print(f"    Input: {error['input']}")
        raise


def test_element_types():
    """Test that position data validates against Pydantic model"""
    data = FplApiDataRaw()

    try:
        element_types = [
            ElementType.model_validate(et) for et in data.element_types_json
        ]
        print(f"Successfully validated {len(element_types)} element types")

        assert len(element_types) == 4, (
            f"Expected 4 positions, got {len(element_types)}"
        )

        # Check position IDs are correct
        position_ids = {et.id for et in element_types}
        assert position_ids == {1, 2, 3, 4}, f"Unexpected position IDs: {position_ids}"

    except ValidationError as e:
        print("Element types validation failed:")
        for error in e.errors():
            field = ".".join(str(x) for x in error["loc"])
            print(f"  - {field}: {error['msg']}")
        raise


def test_teams():
    """Test that team data validates against Pydantic model"""
    data = FplApiDataRaw()

    try:
        teams = [Team.model_validate(t) for t in data.teams_json]
        print(f"Successfully validated {len(teams)} teams")

        assert len(teams) == 20, f"Expected 20 teams, got {len(teams)}"

        # Check team IDs are sequential
        team_ids = sorted([t.id for t in teams])
        assert team_ids == list(range(1, 21)), f"Non-sequential team IDs: {team_ids}"

    except ValidationError as e:
        print("Teams validation failed:")
        for error in e.errors():
            field = ".".join(str(x) for x in error["loc"])
            print(f"  - {field}: {error['msg']}")
        raise
