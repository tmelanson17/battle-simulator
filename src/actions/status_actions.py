"""
Enhanced Actions that integrate with the status effect listener system.

This module extends the existing actions to work with status effect listeners,
particularly for moves like Thunder Wave that apply status conditions.
"""

from typing import Optional

from src.actions.actions import Action
from src.state.pokestate import Player, BattleState, PokemonState
from src.state.pokestate_defs import PokemonId, Status
from src.events.event_queue import EventQueue
from src.events.game_state import GameState
from src.events.listener import ListenerManager, Listener
from src.events.status_listeners import (
    StatusListener, 
    ParalysisListener, 
    PoisonListener, 
    ToxicListener, 
    BurnListener, 
    SleepListener, 
    FreezeListener
)
from src.dex.moves import get_move_by_name

class ApplyStatusAction(Action):
    """Manages status effect listeners for Pokemon"""
    
    def __init__(self, player: Player, pokemon_idx: int, status: Status):
        self.status = status
        self.player = player
        self.pokemon_idx = pokemon_idx
        self.listener_manager: Optional[ListenerManager] = None
        self.battle_state: Optional[BattleState] = None

    def _can_apply_status(self, pokemon: 'PokemonState') -> bool:
        """Check if a status can be applied (prevents multiple status conditions)"""
        if pokemon.status != Status.NONE and pokemon.status != Status.FAINTED:
            print(f"{pokemon.name} already has a status condition!")
            return False
        return True

    def _apply_status(self, pokemon_id: PokemonId, status: Status, listener: Listener, message: str = "") -> bool:
        if not self.listener_manager or not self.battle_state:
            raise LookupError("ListenerManager or BattleState not set")
        pokemon = self.battle_state.get_pokemon(pokemon_id)
        if not self._can_apply_status(pokemon):
            return False
        pokemon.status = status
        print(message.format(pokemon.name))
        self.listener_manager.add_listener(pokemon_id, listener)
        return True

    def apply_paralysis(self, pokemon_id: PokemonId) -> bool:
        """Apply paralysis status and create listener"""
        return self._apply_status(pokemon_id, Status.PARALYZED, ParalysisListener(self.player, self.pokemon_idx),
                                   "{} is paralyzed! It may be unable to move!")

    def apply_poison(self, pokemon_id: PokemonId) -> bool:
        """Apply poison status and create listener"""
        return self._apply_status(pokemon_id, Status.POISONED, PoisonListener(self.player, self.pokemon_idx),
                                   "{} was poisoned!")

    def apply_toxic(self, pokemon_id: PokemonId) -> bool:
        """Apply toxic status and create listener"""
        return self._apply_status(pokemon_id, Status.TOXIC, ToxicListener(self.player, self.pokemon_idx),
                                   "{} was badly poisoned!")

    def apply_burn(self, pokemon_id: PokemonId) -> bool:
        """Apply burn status and create listener"""
        return self._apply_status(pokemon_id, Status.BURNED, BurnListener(self.player, self.pokemon_idx),
                                   "{} was burned!")

    def apply_sleep(self, pokemon_id: PokemonId) -> bool:
        """Apply sleep status and create listener"""
        return self._apply_status(pokemon_id, Status.SLEEP, SleepListener(self.player, self.pokemon_idx),
                                   "{} fell asleep!")

    def apply_freeze(self, pokemon_id: PokemonId) -> bool:
        """Apply freeze status and create listener"""
        return self._apply_status(pokemon_id, Status.FROZEN, FreezeListener(self.player, self.pokemon_idx),
                                   "{} was frozen solid!")
                                
    # TODO: Make this step a little cleaner.
    def execute(self, game_state: GameState):
        self.listener_manager = game_state.listener_manager
        self.battle_state = game_state.battle_state
        pokemon_id = (self.player, self.pokemon_idx)
        if self.status == Status.PARALYZED:
            self.apply_paralysis(pokemon_id)
        elif self.status == Status.POISONED:
            self.apply_poison(pokemon_id)
        elif self.status == Status.TOXIC:
            self.apply_toxic(pokemon_id)
        elif self.status == Status.BURNED:
            self.apply_burn(pokemon_id)
        elif self.status == Status.SLEEP:
            self.apply_sleep(pokemon_id)
        elif self.status == Status.FROZEN:
            self.apply_freeze(pokemon_id)
        else:
            raise ValueError(f"Unsupported status: {self.status}")

class CureStatusAction:
    def __init__(self, player: Player, pokemon_idx: int, status: Optional[Status]):
        self.pokemon_id: PokemonId = (player, pokemon_idx)
        self.status = status


    def _applicable(self, battle_state: BattleState) -> bool:
        """Check if the status can be cured"""
        player, pokemon = self.pokemon_id
        mon = battle_state.get_player(player).pk_list[pokemon]

        if self.status is None:
            return mon.statused
        else:
            return mon.status == self.status

    def cure_status(self, battle_state: BattleState, listener_manager: ListenerManager):
        """Remove status and clean up listeners"""
        player, pokemon_idx = self.pokemon_id
        if self._applicable(battle_state):
            listener_manager.remove_listener(self.pokemon_id, lambda l: isinstance(l, StatusListener) and (self.status is None or l.status == self.status))