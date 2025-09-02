import random

from dataclasses import dataclass, field
from abc import ABC, abstractmethod

from typing import Tuple, Optional
from src.actions.actions import Action, SwitchIn
from src.actions.choose_action import ChooseAction
from src.events.event_queue import EventQueue
from src.events.listener import Listener, ListenerManager
from src.events.priority import Priority, MAX_PRIORITY, MIN_PRIORITY
from src.state.pokestate import PokemonState, BattleState, PlayerState, Player, print_battle_state
from src.events.game_state import GameState


class DeathListener(Listener[BattleState]):
    datatype = BattleState
    
    def __init__(self, player: Player, slot: int):
        self.player = player
        self.slot = slot

    # TODO: Listener needs to make sure it doesn't get put in listen loop.
    def on_event(self, input: BattleState, event_queue: EventQueue):
        
        mon = input.get_player(self.player).get_active_mon(self.slot)
        if mon and mon.fainted:
            print(f"{mon.name} fainted!")
            # TODO: incorporate source slot into the action (as it will be needed)
            event_queue.remove_event(lambda event: event.player == self.player)
            event_queue.add_event(ChooseAction(self.player), Priority(MIN_PRIORITY, mon.speed.current_stat))

# Possible actions:
# - Choose (options) : If the player needs to make a decision
# - Order (action queue) : Orders the action queue by order of events
# - Attack (target) : Executes an attack on the specified target
# - Effect (target) : Executes stat or status effect on the specified target


class BattleManager:
    def __init__(self, battle_state: BattleState):
        self._turn_counter = -1
        self._game_state = GameState(
            battle_state,
            EventQueue[Action, Priority](),
            ListenerManager(),
        )

    def _turn_ended(self) -> bool:
        return self._game_state.event_queue.empty()

    def _add_death_listeners(self):
        for player in [Player.PLAYER_1, Player.PLAYER_2]:
            # Register death listeners for each player's Pokemon
            for slot in range(len(battle_state.get_player(player).active_mons)):
                pokemon_id = (player, battle_state.get_player(player).active_mons[slot])
                self._game_state.listener_manager.add_listener(pokemon_id, DeathListener(player, slot))

    def execution_loop(self):
        self._add_death_listeners()

        self._game_state.event_queue.add_event(SwitchIn(Player.PLAYER_1, 0), Priority(0, 0))
        self._game_state.event_queue.add_event(SwitchIn(Player.PLAYER_2, 0), Priority(0, 0))
        # Implement the logic for executing a turn in the battle
        while not self._game_state.battle_state.is_finished():
            if self._turn_ended():
                self._turn_counter += 1
                self._game_state.event_queue.add_event(ChooseAction(Player.PLAYER_1), Priority(MAX_PRIORITY, 0))
                self._game_state.event_queue.add_event(ChooseAction(Player.PLAYER_2), Priority(MAX_PRIORITY, 0))
                print(f"Turn {self._turn_counter} starts!")
                print_battle_state(self._game_state.battle_state, f"Turn {self._turn_counter}")
                print("=========")
            priority, next_action = self._game_state.event_queue.get_next_event()
            if not isinstance(next_action, Action):
                self._game_state.listener_manager.listen(self._game_state.battle_state, self._game_state.event_queue)
            next_action.execute(self._game_state)
            if not isinstance(next_action, ChooseAction):
                self._game_state.listener_manager.listen(self._game_state.battle_state, self._game_state.event_queue)

            # TODO : Reorder action queue based on new priorities
            self._game_state.event_queue.reorder()


if __name__ == "__main__":
    from src.state.pokestate import create_default_battle_state, MoveState
    battle_state = create_default_battle_state(
        ["Pikachu", "Bulbasaur", "Charmander"],
        ["Squirtle", "Pidgey", "Rattata"],
        [
            ["Thunderbolt", "Quick Attack", "Thunder Wave", "Seismic Toss"],
            ["Vine Whip", "Tackle", "Razor Leaf", "Sleep Powder"],
            ["Ember", "Scratch", "Growl", "Leer"]
        ],
        [
            ["Water Gun", "Tackle", "Bubble"],
            ["Quick Attack", "Gust", "Sand Attack"],
            ["Quick Attack", "Tackle", "Tail Whip"]
        ]
    )
    battle_manager = BattleManager(battle_state)
    battle_manager.execution_loop()