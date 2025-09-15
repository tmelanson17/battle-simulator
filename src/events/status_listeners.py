"""
Status Effect Listeners

This module contains listeners that implement status effects like paralysis, poison, etc.
using the event system. These listeners respond to various game events and modify
behavior accordingly.
"""

import random
from abc import ABC, abstractmethod

from src.events.listener import Listener, ListenerManager
from src.events.event_queue import EventQueue
from src.state.pokestate import BattleState, PokemonState, Player
from src.state.pokestate_defs import PokemonId, Status


class StatusListener(Listener, ABC):
    """Base class for status effect listeners"""

    def __init__(self, player: Player, pokemon_idx: int, status: Status):
        self.player = player
        self.pokemon_idx = pokemon_idx
        self.status = status
        self.active = True

    def get_pokemon(self, battle_state: BattleState) -> PokemonState:
        """Get the Pokemon this listener is attached to"""
        return battle_state.get_player(self.player).pk_list[self.pokemon_idx]

    def should_remove(self, battle_state: BattleState) -> bool:
        """Check if this listener should be removed (e.g., status cured)"""
        pokemon = self.get_pokemon(battle_state)
        return pokemon.fainted or pokemon.status != self.status


class ParalysisListener(Listener[BattleState]):
    """Comprehensive listener that handles all paralysis effects"""

    datatype = BattleState
    PARALYZE_CHANCE: float = 0.6  # 30% chance to be unable to move
    SPEED_REDUCTION: float = 0.25

    def __init__(self, player: Player, pokemon_idx: int):
        self.player = player
        self.pokemon_idx = pokemon_idx
        self.speed_reduced = False
        self.original_base_speed = None

    # TODO: Mark itself for deletion if it status is removed.
    def on_event(self, input: BattleState, event_queue: EventQueue) -> bool:
        pokemon = input.get_player(self.player).pk_list[self.pokemon_idx]

        if pokemon.status == Status.PARALYZED:
            # Handle speed reduction
            self._handle_speed_reduction(pokemon)
            # Handle move prevention
            self._handle_move_prevention(event_queue, pokemon)
            return True
        elif pokemon.status != Status.PARALYZED and self.speed_reduced:
            # Restore speed if no longer paralyzed
            self._restore_speed(pokemon)
            return False

    def _handle_speed_reduction(self, pokemon: PokemonState):
        """Apply speed reduction when paralyzed"""
        if not self.speed_reduced:
            self.original_base_speed = pokemon.speed.base
            new_base_speed = int(self.original_base_speed * self.SPEED_REDUCTION)
            pokemon.speed.base = new_base_speed
            self.speed_reduced = True
            print(
                f"{pokemon.name}'s speed was reduced due to paralysis! ({self.original_base_speed} -> {new_base_speed})"
            )

    def _restore_speed(self, pokemon: PokemonState):
        """Restore original speed when paralysis is cured"""
        if self.original_base_speed is not None:
            pokemon.speed.base = self.original_base_speed
            self.speed_reduced = False
            print(f"{pokemon.name}'s speed was restored!")

    def _handle_move_prevention(self, event_queue: EventQueue, pokemon: PokemonState):
        """30% chance to prevent move actions"""
        all_events = event_queue.get_all_events()
        for priority_item in all_events:
            action = priority_item.event
            if (
                action.__class__.__name__ == "MoveAction"
                and action.player == self.player
                and action.src_idx == self.pokemon_idx
            ):
                if random.random() < self.PARALYZE_CHANCE:
                    print(f"{pokemon.name} is paralyzed and can't move!")
                    event_queue.remove_event(lambda event: event == action)
                    break


class PoisonListener(Listener[BattleState]):
    """Listener that handles poison damage"""

    datatype = BattleState

    def __init__(self, player: Player, pokemon_idx: int):
        self.player = player
        self.pokemon_idx = pokemon_idx

    def on_event(self, input: BattleState, event_queue: EventQueue) -> bool:
        pokemon = input.get_player(self.player).pk_list[self.pokemon_idx]

        if pokemon.status == Status.POISONED and not pokemon.fainted:
            # Apply 12.5% damage
            damage = max(1, int(pokemon.hp_max * 0.125))
            pokemon.hp = max(0, pokemon.hp - damage)
            print(f"{pokemon.name} is hurt by poison! (-{damage} HP)")

            if pokemon.hp <= 0:
                print(f"{pokemon.name} fainted from poison!")
                return False
        return True


class ToxicListener(Listener[BattleState]):
    """Listener that handles toxic damage (increasing each turn)"""

    datatype = BattleState

    def __init__(self, player: Player, pokemon_idx: int):
        self.player = player
        self.pokemon_idx = pokemon_idx
        self.toxic_counter = 1

    def on_event(self, input: BattleState, event_queue: EventQueue) -> bool:
        pokemon = input.get_player(self.player).pk_list[self.pokemon_idx]

        if pokemon.status != Status.TOXIC:
            return False

        if not pokemon.active:
            self.toxic_counter = 1
            return True

        # Damage increases each turn: 6.25% * turn_number
        damage = max(1, int(pokemon.hp_max * 0.0625 * self.toxic_counter))
        pokemon.hp = max(0, pokemon.hp - damage)
        print(
            f"{pokemon.name} is badly poisoned! (-{damage} HP, turn {self.toxic_counter})"
        )

        self.toxic_counter += 1
        return True


class BurnListener(Listener[BattleState]):
    """Comprehensive listener that handles all burn effects"""

    datatype = BattleState

    def __init__(self, player: Player, pokemon_idx: int):
        self.player = player
        self.pokemon_idx = pokemon_idx
        self.attack_reduced = False
        self.original_base_attack = None

    def on_event(self, input: BattleState, event_queue: EventQueue) -> bool:
        pokemon = input.get_player(self.player).pk_list[self.pokemon_idx]

        if pokemon.status == Status.BURNED:
            # Handle attack reduction
            self._handle_attack_reduction(pokemon)
            # Handle burn damage
            self._handle_burn_damage(pokemon)
            return True
        elif self.attack_reduced:
            # Restore attack if no longer burned
            self._restore_attack(pokemon)
            return False
        else:
            return False

    def _handle_attack_reduction(self, pokemon: PokemonState):
        """Apply attack reduction when burned"""
        if not self.attack_reduced:
            self.original_base_attack = pokemon.attack.base
            new_base_attack = int(self.original_base_attack * 0.5)
            pokemon.attack.base = new_base_attack
            self.attack_reduced = True
            print(
                f"{pokemon.name}'s attack was reduced due to burn! ({self.original_base_attack} -> {new_base_attack})"
            )

    def _restore_attack(self, pokemon: PokemonState):
        """Restore original attack when burn is cured"""
        if self.original_base_attack is not None:
            pokemon.attack.base = self.original_base_attack
            self.attack_reduced = False
            print(f"{pokemon.name}'s attack was restored!")

    def _handle_burn_damage(self, pokemon: PokemonState):
        """Apply burn damage"""
        if not pokemon.fainted:
            damage = max(1, int(pokemon.hp_max * 0.125))
            pokemon.hp = max(0, pokemon.hp - damage)
            print(f"{pokemon.name} is hurt by its burn! (-{damage} HP)")

            if pokemon.hp <= 0:
                print(f"{pokemon.name} fainted from its burn!")


class SleepListener(Listener[BattleState]):
    """Listener that handles sleep immobility and wake-up"""

    datatype = BattleState

    def __init__(self, player: Player, pokemon_idx: int):
        self.player = player
        self.pokemon_idx = pokemon_idx
        self.sleep_turns_remaining = random.randint(1, 3)

    def on_event(self, input: BattleState, event_queue: EventQueue) -> bool:
        pokemon = input.get_player(self.player).pk_list[self.pokemon_idx]

        if pokemon.status == Status.SLEEP:
            if self.sleep_turns_remaining <= 0:
                pokemon.status = Status.NONE
                print(f"{pokemon.name} woke up!")
                return False
            else:
                print(
                    f"{pokemon.name} is fast asleep! ({self.sleep_turns_remaining} turns left)"
                )
                # Remove all move actions while asleep
                self._remove_all_moves(event_queue, pokemon)

                # Decrease sleep counter
                self.sleep_turns_remaining -= 1
                return True
        else:
            return False

    def _remove_all_moves(self, event_queue: EventQueue, pokemon: PokemonState):
        """Remove all move actions for this Pokemon"""

        def is_move_from_pokemon(event):
            return (
                event.__class__.__name__ == "MoveAction"
                and event.player == self.player
                and event.src_idx == self.pokemon_idx
            )

        event_queue.remove_event(is_move_from_pokemon)


class FreezeListener(Listener[BattleState]):
    """Listener that handles freeze immobility and thaw chance"""

    datatype = BattleState

    def __init__(self, player: Player, pokemon_idx: int):
        self.player = player
        self.pokemon_idx = pokemon_idx

    def on_event(self, input: BattleState, event_queue: EventQueue) -> bool:
        pokemon = input.get_player(self.player).pk_list[self.pokemon_idx]

        if pokemon.status == Status.FROZEN:
            # 20% chance to thaw out
            if random.random() < 0.2:
                pokemon.status = Status.NONE
                print(f"{pokemon.name} thawed out!")
                return False

            # Still frozen - remove all move actions
            print(f"{pokemon.name} is frozen solid!")
            self._remove_all_moves(event_queue, pokemon)
            return True
        else:
            return False

    def _remove_all_moves(self, event_queue: EventQueue, pokemon: PokemonState):
        """Remove all move actions for this Pokemon"""

        def is_move_from_pokemon(event):
            return (
                event.__class__.__name__ == "MoveAction"
                and event.player == self.player
                and event.src_idx == self.pokemon_idx
            )

        event_queue.remove_event(is_move_from_pokemon)


class CleanupSwitchoutListeners:
    def __init__(
        self, player: Player, pokemon_idx: int, listener_manager: ListenerManager
    ):
        self.pokemon_id: PokemonId = (player, pokemon_idx)
        self.listener_manager = listener_manager

    def cleanup_fainted_pokemon(self, pokemon_id: PokemonId):
        """Clean up all listeners when a Pokemon faints"""
        self.listener_manager.remove_listener(
            pokemon_id, lambda l: isinstance(l, StatusListener)
        )
