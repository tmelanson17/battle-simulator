from abc import ABC, abstractmethod

from src.events.event_queue import EventQueue
from src.events.game_state import GameState
from src.state.pokestate import BattleState, PlayerState, PokemonState
from src.state.pokestate import Player
from src.actions.effects import Effect, from_move

class Action(ABC):
    def __init__(self, player: Player):
        self.player = player

    @abstractmethod
    def execute(self, game_state: GameState):
        pass

class SwitchIn(Action):
    def __init__(self, player: 'Player', new_idx: int):
        super().__init__(player)
        self.pokemon_idx = new_idx

    # TODO: Apply switch-in effects
    def execute(self, game_state: GameState):
        game_state.battle_state.get_player(self.player).switch_pokemon(0, self.pokemon_idx)


class EffectAction(Action):
    def __init__(self, player: 'Player', effect: 'Effect', target_idx: int):
        super().__init__(player)
        self.effect = effect
        self.target_idx = target_idx

    def execute(self, game_state: GameState):
        target = game_state.battle_state.get_player(self.player).get_active_mon(self.target_idx)
        if target:
            # Apply the effect to the target
            self.effect.apply(target)
            print(f"Applied {self.effect} to {target.name}!")

class DamageAction(Action):
    def __init__(self, player: 'Player', damage: int, src_idx: int, target_idx: int):
        super().__init__(player)
        self.player = player
        self.damage = damage
        self.src_idx = src_idx
        self.target_idx = target_idx

    def execute(self, game_state: GameState):
        target_mon = game_state.battle_state.get_opponent(self.player).get_active_mon(self.target_idx)
        if target_mon and not target_mon.fainted:
            target_mon.hp = target_mon.hp - self.damage
            print(f"Dealt {self.damage} damage!")
        else:
            print("Damage had no target!")

