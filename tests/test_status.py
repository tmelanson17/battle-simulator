"""
Integration tests for status conditions: infliction via status moves and
end-of-turn effects applied by listeners.

Two layers are tested:
  1. Infliction  – a status move (e.g. Thunder Wave) sets the target's status.
  2. Effects     – the registered listener fires each turn and applies the
                   appropriate side-effect (damage, speed cut, move removal …).
"""

import pytest
from unittest.mock import patch

from src.state.pokestate import create_default_battle_state
from src.state.pokestate_defs import Player, Status
from src.state.field import FieldState, FieldSide
from src.events.game_state import GameState
from src.events.event_queue import EventQueue
from src.events.listener import ListenerManager
from src.actions.actions import SwitchIn
from src.actions.move_action import MoveAction
from src.actions.status_actions import ApplyStatusAction
from src.events.status_listeners import BattleState


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
    """Drain and execute every action currently in the event queue."""
    while not gs.event_queue.empty():
        _priority, action = gs.event_queue.get_next_event()
        action.execute(gs)


def queue_has_move_for(gs, player, src_idx) -> bool:
    """Return True if the event queue contains a MoveAction for the given pokemon."""
    return any(
        item.event.__class__.__name__ == "MoveAction"
        and item.event.player == player
        and item.event.src_idx == src_idx
        for item in gs.event_queue.get_all_events()
    )


# ---------------------------------------------------------------------------
# Status infliction via status moves
# ---------------------------------------------------------------------------

def test_thunder_wave_inflicts_paralysis():
    """Thunder Wave applied via MoveAction sets the target's status to PARALYZED."""
    gs = make_game_state(
        ["Pikachu", "Rattata"], ["Bulbasaur", "Charmander"],
        [["Thunder Wave", "Tackle"], ["Quick Attack", "Tackle"]],
        [["Vine Whip", "Tackle"], ["Ember", "Scratch"]],
    )
    target = gs.battle_state.get_player(Player.PLAYER_2).pk_list[0]

    MoveAction(Player.PLAYER_1, 0, 0, 0).execute(gs)
    process_queue(gs)

    assert target.status == Status.PARALYZED


def test_stun_spore_inflicts_paralysis():
    """Stun Spore applied via MoveAction sets the target's status to PARALYZED."""
    gs = make_game_state(
        ["Bulbasaur", "Rattata"], ["Charmander", "Squirtle"],
        [["Stun Spore", "Vine Whip"], ["Quick Attack", "Tackle"]],
        [["Ember", "Scratch"], ["Water Gun", "Tackle"]],
    )
    target = gs.battle_state.get_player(Player.PLAYER_2).pk_list[0]

    MoveAction(Player.PLAYER_1, 0, 0, 0).execute(gs)
    process_queue(gs)

    assert target.status == Status.PARALYZED


def test_sleep_powder_inflicts_sleep():
    """Sleep Powder applied via MoveAction sets the target's status to SLEEP."""
    gs = make_game_state(
        ["Bulbasaur", "Rattata"], ["Charmander", "Squirtle"],
        [["Sleep Powder", "Vine Whip"], ["Quick Attack", "Tackle"]],
        [["Ember", "Scratch"], ["Water Gun", "Tackle"]],
    )
    target = gs.battle_state.get_player(Player.PLAYER_2).pk_list[0]

    MoveAction(Player.PLAYER_1, 0, 0, 0).execute(gs)
    process_queue(gs)

    assert target.status == Status.SLEEP


def test_poison_powder_inflicts_poison():
    """Poison Powder applied via MoveAction sets the target's status to POISONED.

    NOTE: This test will fail if gen1_moves.py defines the effect value as
    'POISON' instead of 'POISONED', since Status('poison') is not a valid
    Status enum value (the correct value is 'poisoned').
    """
    gs = make_game_state(
        ["Bulbasaur", "Rattata"], ["Charmander", "Squirtle"],
        [["Poison Powder", "Vine Whip"], ["Quick Attack", "Tackle"]],
        [["Ember", "Scratch"], ["Water Gun", "Tackle"]],
    )
    target = gs.battle_state.get_player(Player.PLAYER_2).pk_list[0]

    MoveAction(Player.PLAYER_1, 0, 0, 0).execute(gs)
    process_queue(gs)

    assert target.status == Status.POISONED


def test_status_move_does_not_overwrite_existing_status():
    """A Pokemon that already has a status cannot have a second status applied."""
    gs = make_game_state(
        ["Pikachu", "Rattata"], ["Bulbasaur", "Charmander"],
        [["Thunder Wave", "Tackle"], ["Quick Attack", "Tackle"]],
        [["Vine Whip", "Tackle"], ["Ember", "Scratch"]],
    )
    target = gs.battle_state.get_player(Player.PLAYER_2).pk_list[0]
    # Pre-apply burn manually.
    target.status = Status.BURNED

    MoveAction(Player.PLAYER_1, 0, 0, 0).execute(gs)
    process_queue(gs)

    # Status should remain BURNED, not change to PARALYZED.
    assert target.status == Status.BURNED


# ---------------------------------------------------------------------------
# Burn effects (BurnListener)
# ---------------------------------------------------------------------------

def test_burn_deals_12_5_percent_damage_per_turn():
    """A burned Pokemon loses 12.5% of its max HP at end of turn."""
    gs = make_game_state(
        ["Rattata", "Pikachu"], ["Bulbasaur", "Charmander"],
        [["Quick Attack", "Tackle"], ["Thunderbolt", "Quick Attack"]],
        [["Vine Whip", "Tackle"], ["Ember", "Scratch"]],
    )
    rattata = gs.battle_state.get_player(Player.PLAYER_1).pk_list[0]
    original_hp = rattata.hp_max

    ApplyStatusAction(Player.PLAYER_1, 0, Status.BURNED).execute(gs)
    assert rattata.status == Status.BURNED

    gs.listener_manager.listen(gs.battle_state, gs.event_queue)

    expected_damage = max(1, int(original_hp * 0.125))
    assert rattata.hp == original_hp - expected_damage


def test_burn_halves_attack_stat():
    """Applying burn halves the Pokemon's base attack stat."""
    gs = make_game_state(
        ["Rattata", "Pikachu"], ["Bulbasaur", "Charmander"],
        [["Quick Attack", "Tackle"], ["Thunderbolt", "Quick Attack"]],
        [["Vine Whip", "Tackle"], ["Ember", "Scratch"]],
    )
    rattata = gs.battle_state.get_player(Player.PLAYER_1).pk_list[0]
    original_attack = rattata.attack

    ApplyStatusAction(Player.PLAYER_1, 0, Status.BURNED).execute(gs)
    gs.listener_manager.listen(gs.battle_state, gs.event_queue)

    assert rattata.attack == int(original_attack * 0.5)


def test_burn_deals_damage_each_successive_turn():
    """Burn deals 12.5% damage on the first turn and again on the second turn."""
    gs = make_game_state(
        ["Rattata", "Pikachu"], ["Bulbasaur", "Charmander"],
        [["Quick Attack", "Tackle"], ["Thunderbolt", "Quick Attack"]],
        [["Vine Whip", "Tackle"], ["Ember", "Scratch"]],
    )
    rattata = gs.battle_state.get_player(Player.PLAYER_1).pk_list[0]
    original_hp = rattata.hp_max
    burn_damage = max(1, int(original_hp * 0.125))

    ApplyStatusAction(Player.PLAYER_1, 0, Status.BURNED).execute(gs)
    gs.listener_manager.listen(gs.battle_state, gs.event_queue)  # turn 1
    gs.listener_manager.listen(gs.battle_state, gs.event_queue)  # turn 2

    assert rattata.hp == original_hp - burn_damage * 2


# ---------------------------------------------------------------------------
# Poison effects (PoisonListener)
# ---------------------------------------------------------------------------

def test_poison_deals_12_5_percent_damage_per_turn():
    """A poisoned Pokemon loses 12.5% of its max HP at end of turn."""
    gs = make_game_state(
        ["Rattata", "Pikachu"], ["Bulbasaur", "Charmander"],
        [["Quick Attack", "Tackle"], ["Thunderbolt", "Quick Attack"]],
        [["Vine Whip", "Tackle"], ["Ember", "Scratch"]],
    )
    rattata = gs.battle_state.get_player(Player.PLAYER_1).pk_list[0]
    original_hp = rattata.hp_max

    ApplyStatusAction(Player.PLAYER_1, 0, Status.POISONED).execute(gs)
    gs.listener_manager.listen(gs.battle_state, gs.event_queue)

    expected_damage = max(1, int(original_hp * 0.125))
    assert rattata.hp == original_hp - expected_damage


def test_poison_deals_damage_each_successive_turn():
    """Poison deals the same flat damage every turn (not escalating)."""
    gs = make_game_state(
        ["Rattata", "Pikachu"], ["Bulbasaur", "Charmander"],
        [["Quick Attack", "Tackle"], ["Thunderbolt", "Quick Attack"]],
        [["Vine Whip", "Tackle"], ["Ember", "Scratch"]],
    )
    rattata = gs.battle_state.get_player(Player.PLAYER_1).pk_list[0]
    original_hp = rattata.hp_max
    poison_damage = max(1, int(original_hp * 0.125))

    ApplyStatusAction(Player.PLAYER_1, 0, Status.POISONED).execute(gs)
    gs.listener_manager.listen(gs.battle_state, gs.event_queue)  # turn 1
    gs.listener_manager.listen(gs.battle_state, gs.event_queue)  # turn 2

    assert rattata.hp == original_hp - poison_damage * 2


# ---------------------------------------------------------------------------
# Toxic effects (ToxicListener)
# ---------------------------------------------------------------------------

def test_toxic_deals_escalating_damage():
    """Badly poisoned (Toxic) damage escalates: 6.25% on turn 1, 12.5% on turn 2."""
    gs = make_game_state(
        ["Rattata", "Pikachu"], ["Bulbasaur", "Charmander"],
        [["Quick Attack", "Tackle"], ["Thunderbolt", "Quick Attack"]],
        [["Vine Whip", "Tackle"], ["Ember", "Scratch"]],
    )
    rattata = gs.battle_state.get_player(Player.PLAYER_1).pk_list[0]
    rattata.active = True  # ToxicListener skips damage when not active
    original_hp = rattata.hp_max

    ApplyStatusAction(Player.PLAYER_1, 0, Status.TOXIC).execute(gs)

    # Turn 1: 6.25% * 1
    gs.listener_manager.listen(gs.battle_state, gs.event_queue)
    t1_damage = max(1, int(original_hp * 0.0625 * 1))
    assert rattata.hp == original_hp - t1_damage

    # Turn 2: 6.25% * 2 additional
    gs.listener_manager.listen(gs.battle_state, gs.event_queue)
    t2_damage = max(1, int(original_hp * 0.0625 * 2))
    assert rattata.hp == original_hp - t1_damage - t2_damage


# ---------------------------------------------------------------------------
# Sleep effects (SleepListener)
# ---------------------------------------------------------------------------

def test_sleep_removes_pending_move_from_queue():
    """A sleeping Pokemon's queued MoveAction is removed by the SleepListener."""
    gs = make_game_state(
        ["Rattata", "Pikachu"], ["Bulbasaur", "Charmander"],
        [["Quick Attack", "Tackle"], ["Thunderbolt", "Quick Attack"]],
        [["Vine Whip", "Tackle"], ["Ember", "Scratch"]],
    )

    ApplyStatusAction(Player.PLAYER_1, 0, Status.SLEEP).execute(gs)

    # Force at least one turn of sleep so the listener doesn't immediately wake.
    from src.events.status_listeners import SleepListener
    for listener in gs.listener_manager.listeners[BattleState]:
        if isinstance(listener, SleepListener):
            listener.sleep_turns_remaining = 2

    # Enqueue a move for the sleeping Pokemon.
    from src.events.priority import Priority
    gs.event_queue.add_event(
        MoveAction(Player.PLAYER_1, 0, 0, 0),
        Priority(0, 100),
    )
    assert queue_has_move_for(gs, Player.PLAYER_1, 0)

    gs.listener_manager.listen(gs.battle_state, gs.event_queue)

    assert not queue_has_move_for(gs, Player.PLAYER_1, 0)


def test_sleep_wears_off_after_turns_expire():
    """A sleeping Pokemon wakes up once its sleep counter reaches zero."""
    gs = make_game_state(
        ["Rattata", "Pikachu"], ["Bulbasaur", "Charmander"],
        [["Quick Attack", "Tackle"], ["Thunderbolt", "Quick Attack"]],
        [["Vine Whip", "Tackle"], ["Ember", "Scratch"]],
    )
    rattata = gs.battle_state.get_player(Player.PLAYER_1).pk_list[0]

    ApplyStatusAction(Player.PLAYER_1, 0, Status.SLEEP).execute(gs)

    # Pin the sleep counter to 1 so it expires after a single listen call.
    from src.events.status_listeners import SleepListener
    for listener in gs.listener_manager.listeners[BattleState]:
        if isinstance(listener, SleepListener):
            listener.sleep_turns_remaining = 1

    gs.listener_manager.listen(gs.battle_state, gs.event_queue)  # counter hits 0
    gs.listener_manager.listen(gs.battle_state, gs.event_queue)  # listener fires wake-up

    assert rattata.status == Status.NONE


# ---------------------------------------------------------------------------
# Paralysis effects (ParalysisListener)
# ---------------------------------------------------------------------------

def test_paralysis_reduces_speed_by_75_percent():
    """Applying paralysis reduces the Pokemon's speed to 25% of its original value."""
    gs = make_game_state(
        ["Rattata", "Pikachu"], ["Bulbasaur", "Charmander"],
        [["Quick Attack", "Tackle"], ["Thunderbolt", "Quick Attack"]],
        [["Vine Whip", "Tackle"], ["Ember", "Scratch"]],
    )
    rattata = gs.battle_state.get_player(Player.PLAYER_1).pk_list[0]
    original_speed = rattata.speed

    ApplyStatusAction(Player.PLAYER_1, 0, Status.PARALYZED).execute(gs)
    gs.listener_manager.listen(gs.battle_state, gs.event_queue)

    assert rattata.speed == int(original_speed * 0.25)


def test_paralysis_can_prevent_move():
    """When paralysed, a Pokemon's queued MoveAction can be removed (chance-based).

    Since move prevention is probabilistic, we mock random.random to always
    return a value that triggers the paralysis check (< PARALYZE_CHANCE = 0.6).
    """
    gs = make_game_state(
        ["Rattata", "Pikachu"], ["Bulbasaur", "Charmander"],
        [["Quick Attack", "Tackle"], ["Thunderbolt", "Quick Attack"]],
        [["Vine Whip", "Tackle"], ["Ember", "Scratch"]],
    )

    ApplyStatusAction(Player.PLAYER_1, 0, Status.PARALYZED).execute(gs)
    # Speed reduction fires on first listen; do that first.
    gs.listener_manager.listen(gs.battle_state, gs.event_queue)

    from src.events.priority import Priority
    gs.event_queue.add_event(
        MoveAction(Player.PLAYER_1, 0, 0, 0),
        Priority(0, 100),
    )
    assert queue_has_move_for(gs, Player.PLAYER_1, 0)

    # Force paralysis to trigger by making random.random return 0.0 (< 0.6).
    with patch("src.events.status_listeners.random.random", return_value=0.0):
        gs.listener_manager.listen(gs.battle_state, gs.event_queue)

    assert not queue_has_move_for(gs, Player.PLAYER_1, 0)
