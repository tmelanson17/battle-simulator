import random

from dataclasses import dataclass, field
from abc import ABC, abstractmethod

from typing import Tuple, Optional
from src.actions.actions import Action, ChooseAction, SwitchIn
from src.events.event_loop import EventLoop
from src.events.priority import Priority
from src.state.pokestate import PokemonState, BattleState, PlayerState, Player, print_battle_state



# Possible actions:
# - Choose (options) : If the player needs to make a decision
# - Order (action queue) : Orders the action queue by order of events
# - Attack (target) : Executes an attack on the specified target
# - Effect (target) : Executes stat or status effect on the specified target

class BattleManager:
    def __init__(self):
        self._action_queue = EventLoop[Action, Priority]()
        self._turn_counter = -1
        
    def execution_loop(self, battle_state: BattleState):
        self._action_queue.add_event(SwitchIn(Player.PLAYER_1, 0), Priority(-1, 0, 0))
        self._action_queue.add_event(SwitchIn(Player.PLAYER_2, 0), Priority(-1, 0, 0))
        self._action_queue.add_event(ChooseAction(Player.PLAYER_1), Priority(0, 8, 0))
        self._action_queue.add_event(ChooseAction(Player.PLAYER_2), Priority(0, 8, 0))
        # Implement the logic for executing a turn in the battle
        while not battle_state.is_finished():
            print("=========")
            priority, next_action = self._action_queue.get_next_event()
            if priority.turn > self._turn_counter:
                print(f"Turn {priority.turn} starts!")
                print_battle_state(battle_state, f"Turn {priority.turn}")
                
            next_action.execute(battle_state, self._action_queue)
            # TODO : Reorder action queue based on new priorities
            


if __name__ == "__main__":
    from src.state.pokestate import create_default_battle_state, MoveState
    battle_manager = BattleManager()
    battle_state = create_default_battle_state(
        ["Pikachu", "Bulbasaur", "Charmander"],
        ["Squirtle", "Pidgey", "Rattata"],
        [
            ["Thunderbolt", "Quick Attack", "Thunder Wave", "Seismic Toss"],
            ["Vine Whip", "Tackle", "Razor Leaf"],
            ["Ember", "Scratch", "Growl", "Leer"]
        ],
        [
            ["Water Gun", "Tackle", "Bubble"],
            ["Quick Attack", "Gust", "Sand Attack"],
            ["Quick Attack", "Tackle", "Tail Whip"]
        ]
    )
    battle_manager.execution_loop(battle_state)