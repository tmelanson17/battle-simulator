import random

from dataclasses import dataclass, field
from abc import ABC, abstractmethod

from queue import PriorityQueue
from typing import Tuple, Optional
from pokestate import PokemonState, BattleState, PlayerState, Player, print_battle_state
from src.state.pokestate_defs import Type, get_effectiveness, calculate_damage
from src.dex.moves import get_move_by_name, Move 


class EventLoop[EventType, PriorityType]:
    @dataclass
    class PriorityItem:
        priority: PriorityType
        event: EventType=field(compare=False)

        def __lt__(self, other: 'PriorityItem') -> bool:
            return self.priority < other.priority
    
    def __init__(self, maxsize=0):
        self._queue = PriorityQueue(maxsize)

    def add_event(self, event: EventType, priority: PriorityType):
        self._queue.put(self.PriorityItem(priority, event))
    
    def get_next_event(self) -> Tuple[PriorityType, EventType]:
        item = self._queue.get()
        return item.priority, item.event

class Action(ABC):
    @abstractmethod
    def execute(self, battle_state: BattleState, event_loop: EventLoop['Action', 'Priority']):
        pass

class SwitchIn(Action):
    def __init__(self, player: 'Player', new_idx: int):
        self.player = player
        self.pokemon_idx = new_idx

    def execute(self, battle_state: BattleState, event_loop: EventLoop['Action', 'Priority']):
        battle_state.get_player(self.player).switch_pokemon(0, self.pokemon_idx)


class DamageAction(Action):
    def __init__(self, player: 'Player', damage: int, src_idx: int, target_idx: int):
        self.player = player
        self.damage = damage
        self.src_idx = src_idx
        self.target_idx = target_idx
    
    def execute(self, battle_state: BattleState, event_loop: EventLoop['Action', 'Priority']):
        target_mon = battle_state.get_opponent(self.player).get_active_mon(self.target_idx)
        if target_mon and not target_mon.fainted:
            target_mon.hp = target_mon.hp - self.damage
            print(f"Dealt {self.damage} damage!")
        else:
            print("Damage had no target!")

class MoveAction(Action):
    def __init__(self, player: Player, move_idx: int, src_idx, target_idx):
        self.player = player
        self.move_idx = move_idx
        self.src_idx = src_idx
        self.target_idx = target_idx

    def calculate_move_damage(self, move: Move) -> int:
        base_power = move.power
        active_mon = battle_state.get_player(self.player).get_active_mon(self.src_idx)
        opponent_mon = battle_state.get_opponent(self.player).get_active_mon(self.target_idx)
        if base_power is None:
            return 0
        effectiveness = 1.0
        if opponent_mon.type1:
            effectiveness *= get_effectiveness(move.type, opponent_mon.type1)
        if opponent_mon.type2:
            effectiveness *= get_effectiveness(move.type, opponent_mon.type2)
        if effectiveness == 0:
            return 0
        stab_multiplier = 1.0
        if move.type == active_mon.type1 or move.type == active_mon.type2:
            stab_multiplier = 1.5
        offensive_stat = active_mon.get_offensive_stat(move.category)
        defensive_stat = opponent_mon.get_defensive_stat(move.category) 
        return calculate_damage(base_power, offensive_stat, defensive_stat, effectiveness, stab_multiplier)

    def execute(self, battle_state: BattleState, event_loop: EventLoop['Action', 'Priority']):
        player = battle_state.get_player(self.player)
        move = player.get_active_mon(self.src_idx).moves[self.move_idx]
        if move.disabled:
            return
        target = battle_state.get_opponent(self.player).get_active_mon(self.target_idx)
        dex_entry = get_move_by_name(move.name)
        print(f"{player.get_active_mon(self.src_idx).name} used {dex_entry.name} on {target.name}!")
        if dex_entry:
            damage = self.calculate_move_damage(dex_entry)
            if damage > 0:
                event_loop.add_event(
                    DamageAction(self.player, damage, self.src_idx, self.target_idx),
                    Priority(0, dex_entry.priority, player.get_active_mon(self.src_idx).speed.current_stat)
                )
            else:
                print(f"It had no effect on {target.name}.")


class ChooseAction(Action):
    def __init__(self, player: 'Player'):
        self.player = player 

    def execute(self, battle_state: BattleState, event_loop: EventLoop['Action', 'Priority']):
        print(f"Player {self.player}")
        turn_count = battle_state.turn_count
        # Get options
        switch_options = battle_state.get_player(self.player).get_available_pokemon()
        if switch_options:
            print("Switch options:")
            for i, pokemon in switch_options:
                print(f"{i + 1}. {pokemon.name} (HP: {pokemon.hp}/{pokemon.hp_max})")
        player_state = battle_state.get_player(self.player)
        for active_idx in player_state.active_mons:
            active_mon = player_state.pk_list[active_idx]
            if active_mon.fainted:
                continue
            move_options = active_mon.moves
            print(f"{active_mon.name} can use the following moves:")
            for i, move in enumerate(move_options):
                disabled = " (DISABLED)" if move.disabled else ""
                print(f"  {i + 1}. {move.name} (PP: {move.pp}/{move.pp_max}){disabled}")
        print()
        self.choose_move(player_state, event_loop, turn_count)
        event_loop.add_event(
            ChooseAction(self.player),
            Priority(turn_count + 1, 9, 0)
        )

    def choose_move(self, player_state: PlayerState, event_loop: EventLoop['Action', 'Priority'], turn_count: int):
        print(f"Choose one of the above moves (either move <x> or switch <x>)")
        move_success = False
        while not move_success:
            try:    
                for i in range(len(player_state.active_mons)):
                    choice = input(f"Your choice for mon {i}: ")
                    active_mon = player_state.get_active_mon(i)
                    if choice.startswith("move"):
                        _, move_str = choice.split()
                        move_idx = int(move_str) - 1
                        if active_mon.valid_move(move_idx):
                            # TODO: Edit target for double battles.
                            move = active_mon.moves[move_idx]
                            event_loop.add_event(
                                MoveAction(self.player, move_idx, i, i),
                                Priority(turn_count, move.move_info.priority if move.move_info else 0, active_mon.speed.current_stat)
                            )
                    elif choice.startswith("switch"):
                        _, switch_str = choice.split()
                        switch_idx = int(switch_str) - 1
                        if switch_idx not in player_state.get_available_pokemon():
                            raise ValueError(f"Cannot switch to {switch_idx + 1} as it is not available.")

                        event_loop.add_event(
                            SwitchIn(self.player, switch_idx),
                            Priority(turn_count, 6, active_mon.speed.current_stat)
                        )
                    else:
                        raise ValueError(f"Invalid choice: {choice}. Please use 'move <x>' or 'switch <x>'.")
                move_success = True
            except ValueError as e:
                print(e)
            except IndexError as e:
                print(e)

class Priority:
    def __init__(self, turn: int, bracket: int, speed: int):
        self.turn = turn
        self.bracket = bracket
        self.speed = speed

    def __lt__(self, other: 'Priority') -> bool:
        # Speed tie resolution.
        if self == other:
            return random.random() > 0.5
        if self.turn != other.turn:
            return self.turn < other.turn
        else:
            return (self.bracket, self.speed) > (other.bracket, other.speed)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Priority):
            raise TypeError("Comparisons should be between Priority instances.")
        return (self.turn, self.bracket, self.speed) == (other.turn, other.bracket, other.speed)


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
    from pokestate import create_default_battle_state, MoveState
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