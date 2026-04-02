"""
Integration tests for fixed-damage moves (Seismic Toss, Night Shade).

These moves deal damage equal to the attacker's level, ignoring stats,
STAB, and type effectiveness — except full type immunity (0×) still blocks them.
"""

from src.state.pokestate import create_default_battle_state
from src.state.pokestate_defs import Player
from src.state.field import FieldState, FieldSide
from src.events.game_state import GameState
from src.events.event_queue import EventQueue
from src.events.listener import ListenerManager
from src.actions.move_action import MoveAction


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_game_state(team1, team2, moves1, moves2):
    battle_state = create_default_battle_state(team1, team2, moves1, moves2)
    return GameState(
        battle_state=battle_state,
        event_queue=EventQueue(),
        listener_manager=ListenerManager(),
        field_state=FieldState(
            player_1_side=FieldSide(hazards={}),
            player_2_side=FieldSide(hazards={}),
        ),
    )


def process_queue(gs):
    while not gs.event_queue.empty():
        _priority, action = gs.event_queue.get_next_event()
        action.execute(gs)


# ---------------------------------------------------------------------------
# Seismic Toss
# ---------------------------------------------------------------------------

def test_seismic_toss_deals_level_damage():
    """Seismic Toss from a level-100 attacker deals exactly 100 HP damage."""
    gs = make_game_state(
        ["Rattata"], ["Bulbasaur"],
        [["Seismic Toss"]], [["Tackle"]],
    )
    target = gs.battle_state.get_player(Player.PLAYER_2).pk_list[0]
    original_hp = target.hp_max

    MoveAction(Player.PLAYER_1, 0, 0, 0).execute(gs)
    process_queue(gs)

    assert target.hp == original_hp - 100


def test_seismic_toss_level_scales_damage():
    """Seismic Toss damage equals the attacker's current level, not a constant."""
    gs = make_game_state(
        ["Rattata"], ["Bulbasaur"],
        [["Seismic Toss"]], [["Tackle"]],
    )
    src_mon = gs.battle_state.get_player(Player.PLAYER_1).pk_list[0]
    target = gs.battle_state.get_player(Player.PLAYER_2).pk_list[0]
    original_hp = target.hp_max

    src_mon.level = 50
    MoveAction(Player.PLAYER_1, 0, 0, 0).execute(gs)
    process_queue(gs)

    assert target.hp == original_hp - 50


def test_seismic_toss_ignores_stab():
    """Seismic Toss from a Fighting-type attacker still deals exactly level damage (no 1.5× STAB)."""
    gs = make_game_state(
        ["Machamp"], ["Bulbasaur"],
        [["Seismic Toss"]], [["Tackle"]],
    )
    target = gs.battle_state.get_player(Player.PLAYER_2).pk_list[0]
    original_hp = target.hp_max

    MoveAction(Player.PLAYER_1, 0, 0, 0).execute(gs)
    process_queue(gs)

    assert target.hp == original_hp - 100


# ---------------------------------------------------------------------------
# Night Shade
# ---------------------------------------------------------------------------

def test_night_shade_deals_level_damage():
    """Night Shade from a level-100 attacker deals exactly 100 HP damage."""
    gs = make_game_state(
        ["Gastly"], ["Bulbasaur"],
        [["Night Shade"]], [["Tackle"]],
    )
    target = gs.battle_state.get_player(Player.PLAYER_2).pk_list[0]
    original_hp = target.hp_max

    MoveAction(Player.PLAYER_1, 0, 0, 0).execute(gs)
    process_queue(gs)

    assert target.hp == original_hp - 100


def test_night_shade_immune_to_normal_type():
    """Night Shade (Ghost-type) cannot hit Normal-type Pokemon (0× effectiveness)."""
    gs = make_game_state(
        ["Gastly"], ["Rattata"],
        [["Night Shade"]], [["Tackle"]],
    )
    target = gs.battle_state.get_player(Player.PLAYER_2).pk_list[0]
    original_hp = target.hp_max

    MoveAction(Player.PLAYER_1, 0, 0, 0).execute(gs)
    process_queue(gs)

    assert target.hp == original_hp
