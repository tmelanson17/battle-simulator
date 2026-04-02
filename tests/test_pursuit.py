"""
Integration tests for Pursuit: a move that fires before the opponent switches out.

If the opponent switches on the same turn Pursuit is used, Pursuit damage is applied
to the switching-out Pokemon before the switch resolves. If no switch occurs, Pursuit
fires as a normal attack at the end of the turn.
"""

from src.state.pokestate import create_default_battle_state
from src.state.pokestate_defs import Player
from src.state.field import FieldState, FieldSide
from src.events.game_state import GameState
from src.events.event_queue import EventQueue
from src.events.listener import ListenerManager
from src.events.pursuit_listener import PursuitListener
from src.events.priority import Priority
from src.actions.actions import SwitchIn, DamageAction
from src.actions.ability_register_action import AbilityRegisterAction
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


def _queue_pursuit(gs, pursuing_player, move_idx=0, src_slot=0, target_slot=0):
    """
    Simulate what ChooseAction does when a player picks Pursuit:
    - Add MoveAction to the event queue (at Pursuit's normal priority 0).
    - Register PursuitListener immediately so it is in place before SwitchIn fires.
    """
    src_mon = gs.battle_state.get_player(pursuing_player).get_active_mon(src_slot)
    gs.event_queue.add_event(
        MoveAction(pursuing_player, move_idx, src_slot, target_slot),
        Priority(0, src_mon.speed),
    )
    gs.listener_manager.add_listener(
        (pursuing_player, src_slot),
        PursuitListener(pursuing_player, gs, move_idx, src_slot, target_slot),
    )


def test_pursuit_fires_before_switch():
    """
    P1 queues Pursuit; P2 switches out on the same turn.
    Pursuit damage is applied to P2's switching-out Pokemon (Bulbasaur) before
    switch_pokemon() resolves, and the pending MoveAction is removed from the queue.
    """
    gs = make_game_state(
        ["Rattata", "Pikachu"], ["Bulbasaur", "Charmander"],
        [["Pursuit", "Quick Attack"], ["Thunderbolt", "Quick Attack"]],
        [["Vine Whip", "Tackle"], ["Ember", "Scratch"]],
    )
    bulbasaur = gs.battle_state.get_player(Player.PLAYER_2).pk_list[0]
    original_hp = bulbasaur.hp_max

    # Simulate ChooseAction: Pursuit queued + listener registered
    _queue_pursuit(gs, Player.PLAYER_1)

    # SwitchIn fires (priority 6 > Pursuit's 0): PursuitListener intercepts
    SwitchIn(Player.PLAYER_2, 1).execute(gs)

    # Bulbasaur (the switching-out Pokemon) took Pursuit damage
    assert bulbasaur.hp < original_hp

    # P2 is now using Charmander
    assert gs.battle_state.get_player(Player.PLAYER_2).get_active_mon(0).name == "Charmander"

    # MoveAction was removed from the queue — Pursuit will not fire again.
    # The only remaining item should be the AbilityRegisterAction from the switch.
    _, remaining = gs.event_queue.get_next_event()
    assert isinstance(remaining, AbilityRegisterAction)
    assert gs.event_queue.empty()


def test_pursuit_only_damages_switching_out_not_switching_in():
    """
    When Pursuit fires before a switch, only the switching-out Pokemon takes damage.
    The Pokemon that switches in should arrive at full HP.
    """
    gs = make_game_state(
        ["Rattata", "Pikachu"], ["Bulbasaur", "Charmander"],
        [["Pursuit", "Quick Attack"], ["Thunderbolt", "Quick Attack"]],
        [["Vine Whip", "Tackle"], ["Ember", "Scratch"]],
    )
    bulbasaur = gs.battle_state.get_player(Player.PLAYER_2).pk_list[0]
    charmander = gs.battle_state.get_player(Player.PLAYER_2).pk_list[1]
    charmander_full_hp = charmander.hp_max

    _queue_pursuit(gs, Player.PLAYER_1)
    SwitchIn(Player.PLAYER_2, 1).execute(gs)

    assert bulbasaur.hp < bulbasaur.hp_max      # switching-out took Pursuit damage
    assert charmander.hp == charmander_full_hp   # switching-in is untouched


def test_pursuit_listener_does_not_persist_after_normal_fire():
    """
    When Pursuit fires normally (opponent didn't switch on Turn 1), the
    PursuitListener must be cleaned up.  If the opponent switches on a later turn
    without Pursuit being used again, no Pursuit damage should occur.
    """
    gs = make_game_state(
        ["Rattata", "Pikachu"], ["Bulbasaur", "Charmander"],
        [["Pursuit", "Quick Attack"], ["Thunderbolt", "Quick Attack"]],
        [["Vine Whip", "Tackle"], ["Ember", "Scratch"]],
    )
    bulbasaur = gs.battle_state.get_player(Player.PLAYER_2).pk_list[0]

    # Turn 1: P1 uses Pursuit, P2 uses Vine Whip (no switch) → Pursuit fires normally
    _queue_pursuit(gs, Player.PLAYER_1)
    MoveAction(Player.PLAYER_2, 0, 0, 0).execute(gs)
    while not gs.event_queue.empty():
        _, action = gs.event_queue.get_next_event()
        action.execute(gs)

    hp_after_turn1 = bulbasaur.hp
    assert hp_after_turn1 < bulbasaur.hp_max  # Pursuit did fire on Turn 1

    # Turn 2: P1 uses something other than Pursuit; P2 switches out
    # The stale PursuitListener must NOT fire again
    SwitchIn(Player.PLAYER_2, 1).execute(gs)

    assert bulbasaur.hp == hp_after_turn1  # no extra Pursuit damage


def test_sleep_prevents_pursuit_before_switch():
    """
    If the Pursuit user is asleep, Pursuit must not fire even when the opponent
    switches out.  The switching-out Pokemon should take no damage and the switch
    should complete normally.
    """
    gs = make_game_state(
        ["Rattata", "Pikachu"], ["Bulbasaur", "Charmander"],
        [["Pursuit", "Quick Attack"], ["Thunderbolt", "Quick Attack"]],
        [["Vine Whip", "Tackle"], ["Ember", "Scratch"]],
    )
    rattata = gs.battle_state.get_player(Player.PLAYER_1).pk_list[0]
    bulbasaur = gs.battle_state.get_player(Player.PLAYER_2).pk_list[0]

    # Put the Pursuit user to sleep
    rattata.status = "sleep"

    _queue_pursuit(gs, Player.PLAYER_1)
    SwitchIn(Player.PLAYER_2, 1).execute(gs)

    assert bulbasaur.hp == bulbasaur.hp_max  # no Pursuit damage
    assert gs.battle_state.get_player(Player.PLAYER_2).get_active_mon(0).name == "Charmander"
    # MoveAction cleaned up; only the AbilityRegisterAction from the switch should remain
    _, remaining = gs.event_queue.get_next_event()
    assert isinstance(remaining, AbilityRegisterAction)
    assert gs.event_queue.empty()


def test_paralysis_removal_prevents_pursuit_before_switch():
    """
    If paralysis (or any other effect) has already removed the Pursuit MoveAction
    from the queue before SwitchIn fires, PursuitListener treats the user as unable
    to act and deals no damage.
    """
    gs = make_game_state(
        ["Rattata", "Pikachu"], ["Bulbasaur", "Charmander"],
        [["Pursuit", "Quick Attack"], ["Thunderbolt", "Quick Attack"]],
        [["Vine Whip", "Tackle"], ["Ember", "Scratch"]],
    )
    bulbasaur = gs.battle_state.get_player(Player.PLAYER_2).pk_list[0]

    _queue_pursuit(gs, Player.PLAYER_1)

    # Simulate paralysis having prevented the move: remove MoveAction from queue
    gs.event_queue.remove_event(
        lambda e: isinstance(e, MoveAction) and e.player == Player.PLAYER_1
    )

    # SwitchIn fires; PursuitListener sees no MoveAction → no damage
    SwitchIn(Player.PLAYER_2, 1).execute(gs)

    assert bulbasaur.hp == bulbasaur.hp_max  # no Pursuit damage
    assert gs.battle_state.get_player(Player.PLAYER_2).get_active_mon(0).name == "Charmander"


def test_pursuit_fires_normally_when_no_switch():
    """
    P1 queues Pursuit; P2 attacks normally (no switch).
    PursuitListener is never triggered.  MoveAction fires at normal priority,
    queuing a DamageAction that hits Bulbasaur.
    """
    gs = make_game_state(
        ["Rattata", "Pikachu"], ["Bulbasaur", "Charmander"],
        [["Pursuit", "Quick Attack"], ["Thunderbolt", "Quick Attack"]],
        [["Vine Whip", "Tackle"], ["Ember", "Scratch"]],
    )
    bulbasaur = gs.battle_state.get_player(Player.PLAYER_2).pk_list[0]
    original_hp = bulbasaur.hp_max

    # Simulate ChooseAction: Pursuit queued + listener registered
    _queue_pursuit(gs, Player.PLAYER_1)

    # P2 uses Vine Whip (no SwitchIn — PursuitListener is never triggered)
    MoveAction(Player.PLAYER_2, 0, 0, 0).execute(gs)

    # Execute all queued events: MoveAction(Pursuit) fires, queues DamageAction, DamageAction executes
    while not gs.event_queue.empty():
        _, action = gs.event_queue.get_next_event()
        action.execute(gs)

    # Bulbasaur took Pursuit damage at normal turn order
    assert bulbasaur.hp < original_hp
