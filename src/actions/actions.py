from abc import ABC, abstractmethod

from src.events.event_queue import EventQueue
from src.events.game_state import GameState
from src.state.pokestate import BattleState, PlayerState, PokemonState
from src.state.pokestate import Player
from src.state.pokestate_defs import MoveHitEvent, SwitchInEvent
from src.state.field import apply_hazards_on_entry
from src.actions.effects import Effect, from_move
from src.events.priority import Priority

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

    def execute(self, game_state: GameState):
        # Remove any ability listeners tied to the outgoing Pokemon's slot
        # before the switch, so they don't fire for the incoming Pokemon.
        game_state.listener_manager.remove_listener_if(
            MoveHitEvent,
            lambda lst: (
                hasattr(lst, "player") and lst.player == self.player
                and hasattr(lst, "slot") and lst.slot == 0
            ),
        )

        # Emit SwitchInEvent BEFORE the switch resolves so listeners like
        # PursuitListener can act on the current (switching-out) Pokemon.
        game_state.listener_manager.listen(
            SwitchInEvent(self.player, 0), game_state.event_queue
        )
        outgoing_mon = game_state.battle_state.get_player(self.player).get_active_mon(0)
        outgoing_mon.reset_boosts()
        game_state.battle_state.get_player(self.player).switch_pokemon(0, self.pokemon_idx)
        apply_hazards_on_entry(self.player, game_state)

        # Queue ability registration — fires at priority 5, after hazards but before moves.
        from src.actions.ability_register_action import AbilityRegisterAction
        incoming_mon = game_state.battle_state.get_player(self.player).get_active_mon(0)
        game_state.event_queue.add_event(
            AbilityRegisterAction(self.player, 0),
            Priority(5, incoming_mon.speed),
        )


class HealAction(Action):
    def __init__(self, player: 'Player', amount: int, target_idx: int):
        super().__init__(player)
        self.amount = amount
        self.target_idx = target_idx

    def execute(self, game_state: GameState):
        target_mon = game_state.battle_state.get_player(self.player).get_active_mon(self.target_idx)
        if target_mon and not target_mon.fainted:
            old_hp = target_mon.hp
            target_mon.hp = target_mon.hp + self.amount
            actual = target_mon.hp - old_hp
            print(f"{target_mon.name} restored {actual} HP!")
        else:
            print("Heal had no target!")


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

