
from src.actions.actions import Action, SwitchIn
from src.actions.move_action import MoveAction
from src.events.game_state import GameState
from src.events.event_queue import EventQueue
from src.events.priority import Priority
from src.state.pokestate import PlayerState
from src.state.pokestate_defs import Player


class ChooseAction(Action):
    def __init__(self, player: 'Player'):
        super().__init__(player)

    def execute(self, game_state: GameState):
        print(f"Player {self.player}")
        turn_count = game_state.battle_state.turn_count
        # Get options
        switch_options = game_state.battle_state.get_player(self.player).get_available_pokemon()
        if switch_options:
            print("Switch options:")
            for i in switch_options:
                pokemon = game_state.battle_state.get_player(self.player).pk_list[i]
                print(f"{i + 1}. {pokemon.name} (HP: {pokemon.hp}/{pokemon.hp_max})")
        player_state = game_state.battle_state.get_player(self.player)
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
        self.choose_move(player_state, game_state.event_queue, turn_count)

    def choose_move(self, player_state: PlayerState, event_loop: EventQueue['Action', 'Priority'], turn_count: int):
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
                                Priority(move.move_info.priority if move.move_info else 0, active_mon.speed.current_stat)
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
                            Priority(6, active_mon.speed.current_stat)
                        )
                    else:
                        raise ValueError(f"Invalid choice: {choice}. Please use 'move <x>' or 'switch <x>'.")
                move_success = True
            except ValueError as e:
                print(e)
            except IndexError as e:
                print(e)