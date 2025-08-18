from abc import ABC, abstractmethod

from src.events.event_loop import EventLoop
from src.events.priority import Priority
from src.state.pokestate import BattleState, PlayerState, PokemonState
from src.state.pokestate import Player
from src.state.pokestate_defs import Type, get_effectiveness, calculate_damage
from src.dex.moves import get_move_by_name, Move 

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

    def calculate_move_damage(self, move: Move, src_mon: PokemonState, target_mon: PokemonState) -> int:
        base_power = move.power
        if base_power is None:
            return 0
        effectiveness = 1.0
        if target_mon.type1:
            effectiveness *= get_effectiveness(move.type, target_mon.type1)
        if target_mon.type2:
            effectiveness *= get_effectiveness(move.type, target_mon.type2)
        if effectiveness == 0:
            return 0
        stab_multiplier = 1.0
        if move.type == src_mon.type1 or move.type == src_mon.type2:
            stab_multiplier = 1.5
        offensive_stat = src_mon.get_offensive_stat(move.category)
        defensive_stat = target_mon.get_defensive_stat(move.category) 
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
            damage = self.calculate_move_damage(dex_entry, player.get_active_mon(self.src_idx), target)
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
            for i in switch_options:
                pokemon = battle_state.get_player(self.player).pk_list[i]
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
                        if active_mon.fainted:
                            raise ValueError(f"Cannot use moves on {active_mon.name} as it is fainted.")
                        _, move_str = choice.split()
                        move_idx = int(move_str) - 1
                        if active_mon.valid_move(move_idx):
                            # TODO: Edit target for double battles.
                            move = active_mon.moves[move_idx]
                            event_loop.add_event(
                                MoveAction(self.player, move_idx, i, i),
                                Priority(turn_count, move.move_info.priority if move.move_info else 0, active_mon.speed.current_stat)
                            )
                        else:
                            raise ValueError(f"Cannot use move {move_idx + 1} on {active_mon.name}.")
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
