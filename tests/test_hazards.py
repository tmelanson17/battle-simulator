"""
Integration tests for field hazards: Stealth Rock, Spikes, Toxic Spikes.

Each test sets hazards directly on the field state and calls SwitchIn to trigger
the on-entry effects, then asserts HP / status changes on the incoming Pokemon.
"""

import pytest
from src.state.pokestate import create_default_battle_state
from src.state.pokestate_defs import Player, Status
from src.state.field import FieldState, FieldSide
from src.events.game_state import GameState
from src.events.event_queue import EventQueue
from src.events.listener import ListenerManager
from src.actions.actions import SwitchIn
from src.actions.move_action import MoveAction


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


# ---------------------------------------------------------------------------
# Stealth Rock
# ---------------------------------------------------------------------------

def test_stealth_rock_neutral_type_takes_12_5_percent():
    """Pikachu (Electric, neutral vs Rock) switches into Stealth Rock → loses 12.5% HP."""
    gs = make_game_state(
        ["Rattata", "Pikachu"], ["Bulbasaur", "Charmander"],
        [["Quick Attack", "Tackle"], ["Thunderbolt", "Quick Attack"]],
        [["Vine Whip", "Tackle"], ["Ember", "Scratch"]],
    )
    pikachu = gs.battle_state.get_player(Player.PLAYER_1).pk_list[1]
    original_hp = pikachu.hp_max
    gs.field_state.get_side(Player.PLAYER_1).hazards["Stealth Rock"] = 1

    SwitchIn(Player.PLAYER_1, 1).execute(gs)

    expected_damage = int(original_hp * 0.125 * 1.0)
    assert pikachu.hp == original_hp - expected_damage


def test_stealth_rock_flying_type_takes_double_damage():
    """Pidgey (Normal/Flying, 2x vs Rock) switches into Stealth Rock → loses 25% HP."""
    gs = make_game_state(
        ["Rattata", "Pidgey"], ["Pikachu", "Bulbasaur"],
        [["Quick Attack", "Tackle"], ["Quick Attack", "Gust"]],
        [["Thunderbolt", "Quick Attack"], ["Vine Whip", "Tackle"]],
    )
    pidgey = gs.battle_state.get_player(Player.PLAYER_1).pk_list[1]
    original_hp = pidgey.hp_max
    gs.field_state.get_side(Player.PLAYER_1).hazards["Stealth Rock"] = 1

    SwitchIn(Player.PLAYER_1, 1).execute(gs)

    expected_damage = int(original_hp * 0.125 * 2.0)
    assert pidgey.hp == original_hp - expected_damage


# ---------------------------------------------------------------------------
# Spikes
# ---------------------------------------------------------------------------

def test_spikes_one_layer_deals_12_5_percent():
    """1 layer of Spikes → incoming Pokemon loses 12.5% HP."""
    gs = make_game_state(
        ["Rattata", "Pikachu"], ["Bulbasaur", "Charmander"],
        [["Quick Attack", "Tackle"], ["Thunderbolt", "Quick Attack"]],
        [["Vine Whip", "Tackle"], ["Ember", "Scratch"]],
    )
    pikachu = gs.battle_state.get_player(Player.PLAYER_1).pk_list[1]
    original_hp = pikachu.hp_max
    gs.field_state.get_side(Player.PLAYER_1).hazards["Spikes"] = 1

    SwitchIn(Player.PLAYER_1, 1).execute(gs)

    expected_damage = int(original_hp * 0.125)
    assert pikachu.hp == original_hp - expected_damage


def test_spikes_two_layers_deals_16_67_percent():
    """2 layers of Spikes → incoming Pokemon loses ~16.67% HP."""
    gs = make_game_state(
        ["Rattata", "Pikachu"], ["Bulbasaur", "Charmander"],
        [["Quick Attack", "Tackle"], ["Thunderbolt", "Quick Attack"]],
        [["Vine Whip", "Tackle"], ["Ember", "Scratch"]],
    )
    pikachu = gs.battle_state.get_player(Player.PLAYER_1).pk_list[1]
    original_hp = pikachu.hp_max
    gs.field_state.get_side(Player.PLAYER_1).hazards["Spikes"] = 2

    SwitchIn(Player.PLAYER_1, 1).execute(gs)

    expected_damage = int(original_hp * (1 / 6))
    assert pikachu.hp == original_hp - expected_damage


def test_spikes_three_layers_deals_25_percent():
    """3 layers of Spikes → incoming Pokemon loses 25% HP."""
    gs = make_game_state(
        ["Rattata", "Pikachu"], ["Bulbasaur", "Charmander"],
        [["Quick Attack", "Tackle"], ["Thunderbolt", "Quick Attack"]],
        [["Vine Whip", "Tackle"], ["Ember", "Scratch"]],
    )
    pikachu = gs.battle_state.get_player(Player.PLAYER_1).pk_list[1]
    original_hp = pikachu.hp_max
    gs.field_state.get_side(Player.PLAYER_1).hazards["Spikes"] = 3

    SwitchIn(Player.PLAYER_1, 1).execute(gs)

    expected_damage = int(original_hp * 0.25)
    assert pikachu.hp == original_hp - expected_damage


def test_spikes_flying_type_immune():
    """Pidgey (Flying-type) switches into Spikes → takes no damage."""
    gs = make_game_state(
        ["Rattata", "Pidgey"], ["Pikachu", "Bulbasaur"],
        [["Quick Attack", "Tackle"], ["Quick Attack", "Gust"]],
        [["Thunderbolt", "Quick Attack"], ["Vine Whip", "Tackle"]],
    )
    pidgey = gs.battle_state.get_player(Player.PLAYER_1).pk_list[1]
    original_hp = pidgey.hp_max
    gs.field_state.get_side(Player.PLAYER_1).hazards["Spikes"] = 3

    SwitchIn(Player.PLAYER_1, 1).execute(gs)

    assert pidgey.hp == original_hp


# ---------------------------------------------------------------------------
# Toxic Spikes
# ---------------------------------------------------------------------------

def test_toxic_spikes_one_layer_inflicts_poison():
    """1 layer of Toxic Spikes → incoming Pokemon is POISONED."""
    gs = make_game_state(
        ["Rattata", "Pikachu"], ["Bulbasaur", "Charmander"],
        [["Quick Attack", "Tackle"], ["Thunderbolt", "Quick Attack"]],
        [["Vine Whip", "Tackle"], ["Ember", "Scratch"]],
    )
    pikachu = gs.battle_state.get_player(Player.PLAYER_1).pk_list[1]
    gs.field_state.get_side(Player.PLAYER_1).hazards["Toxic Spikes"] = 1

    SwitchIn(Player.PLAYER_1, 1).execute(gs)

    assert pikachu.status == Status.POISONED


def test_toxic_spikes_two_layers_inflicts_toxic():
    """2 layers of Toxic Spikes → incoming Pokemon is badly poisoned (TOXIC)."""
    gs = make_game_state(
        ["Rattata", "Pikachu"], ["Bulbasaur", "Charmander"],
        [["Quick Attack", "Tackle"], ["Thunderbolt", "Quick Attack"]],
        [["Vine Whip", "Tackle"], ["Ember", "Scratch"]],
    )
    pikachu = gs.battle_state.get_player(Player.PLAYER_1).pk_list[1]
    gs.field_state.get_side(Player.PLAYER_1).hazards["Toxic Spikes"] = 2

    SwitchIn(Player.PLAYER_1, 1).execute(gs)

    assert pikachu.status == Status.TOXIC


def test_toxic_spikes_poison_type_cleanses_hazard():
    """Bulbasaur (Grass/Poison) switches into Toxic Spikes → absorbs them, takes no status."""
    gs = make_game_state(
        ["Rattata", "Bulbasaur"], ["Pikachu", "Charmander"],
        [["Quick Attack", "Tackle"], ["Vine Whip", "Tackle"]],
        [["Thunderbolt", "Quick Attack"], ["Ember", "Scratch"]],
    )
    bulbasaur = gs.battle_state.get_player(Player.PLAYER_1).pk_list[1]
    gs.field_state.get_side(Player.PLAYER_1).hazards["Toxic Spikes"] = 1

    SwitchIn(Player.PLAYER_1, 1).execute(gs)

    assert bulbasaur.status == Status.NONE
    assert "Toxic Spikes" not in gs.field_state.get_side(Player.PLAYER_1).hazards


# ---------------------------------------------------------------------------
# Hazard removal
# ---------------------------------------------------------------------------

def test_rapid_spin_clears_stealth_rock():
    """Using Rapid Spin removes Stealth Rock; subsequent switch-in takes no damage."""
    gs = make_game_state(
        ["Rattata", "Pikachu"], ["Bulbasaur", "Charmander"],
        [["Rapid Spin", "Tackle"], ["Thunderbolt", "Quick Attack"]],
        [["Vine Whip", "Tackle"], ["Ember", "Scratch"]],
    )
    pikachu = gs.battle_state.get_player(Player.PLAYER_1).pk_list[1]
    gs.field_state.get_side(Player.PLAYER_1).hazards["Stealth Rock"] = 1

    # Rattata uses Rapid Spin (move index 0) — clears P1's hazards
    MoveAction(Player.PLAYER_1, 0, 0, 0).execute(gs)
    assert "Stealth Rock" not in gs.field_state.get_side(Player.PLAYER_1).hazards

    original_hp = pikachu.hp_max
    SwitchIn(Player.PLAYER_1, 1).execute(gs)
    assert pikachu.hp == original_hp


def test_defog_clears_stealth_rock():
    """Using Defog removes Stealth Rock; subsequent switch-in takes no damage."""
    gs = make_game_state(
        ["Rattata", "Pikachu"], ["Bulbasaur", "Charmander"],
        [["Defog", "Tackle"], ["Thunderbolt", "Quick Attack"]],
        [["Vine Whip", "Tackle"], ["Ember", "Scratch"]],
    )
    pikachu = gs.battle_state.get_player(Player.PLAYER_1).pk_list[1]
    gs.field_state.get_side(Player.PLAYER_1).hazards["Stealth Rock"] = 1

    MoveAction(Player.PLAYER_1, 0, 0, 0).execute(gs)
    assert "Stealth Rock" not in gs.field_state.get_side(Player.PLAYER_1).hazards

    original_hp = pikachu.hp_max
    SwitchIn(Player.PLAYER_1, 1).execute(gs)
    assert pikachu.hp == original_hp


# ---------------------------------------------------------------------------
# No hazards / misc
# ---------------------------------------------------------------------------

def test_no_hazards_set_no_damage_on_switch():
    """With no hazards set, switching in takes no damage."""
    gs = make_game_state(
        ["Rattata", "Pikachu"], ["Bulbasaur", "Charmander"],
        [["Quick Attack", "Tackle"], ["Thunderbolt", "Quick Attack"]],
        [["Vine Whip", "Tackle"], ["Ember", "Scratch"]],
    )
    pikachu = gs.battle_state.get_player(Player.PLAYER_1).pk_list[1]
    original_hp = pikachu.hp_max

    SwitchIn(Player.PLAYER_1, 1).execute(gs)

    assert pikachu.hp == original_hp


def test_multiple_hazards_both_apply_on_switch():
    """Stealth Rock + Spikes both deal damage when a Pokemon switches in."""
    gs = make_game_state(
        ["Rattata", "Pikachu"], ["Bulbasaur", "Charmander"],
        [["Quick Attack", "Tackle"], ["Thunderbolt", "Quick Attack"]],
        [["Vine Whip", "Tackle"], ["Ember", "Scratch"]],
    )
    pikachu = gs.battle_state.get_player(Player.PLAYER_1).pk_list[1]
    original_hp = pikachu.hp_max
    gs.field_state.get_side(Player.PLAYER_1).hazards["Stealth Rock"] = 1
    gs.field_state.get_side(Player.PLAYER_1).hazards["Spikes"] = 1

    SwitchIn(Player.PLAYER_1, 1).execute(gs)

    sr_damage = int(original_hp * 0.125 * 1.0)   # neutral Rock vs Electric
    spikes_damage = int(original_hp * 0.125)
    assert pikachu.hp == original_hp - sr_damage - spikes_damage
