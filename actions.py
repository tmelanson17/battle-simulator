from dataclasses import dataclass
from typing import Union, Optional, Tuple

from player import Player
from pokemon import Pokemon
from movedex import Move

@dataclass
class BattleAction:
    """Represents an action taken in battle"""
    player: Player
    move: Move
    priority: int = 0
    target: Optional[Pokemon] = None

    def get_priority(self) -> Tuple[int, int]:
        # TODO: Make sure BattleAction is initialized correctly.
        if not self.player.active_pokemon:
            raise ValueError("Player has no active Pokemon")
        return (self.priority, self.player.active_pokemon.speed)


@dataclass
class SwitchAction:
    player: Player
    pokemon_idx: int
    def get_priority(self) -> Tuple[int, int]:
        return (7, 0)

Action = Union[BattleAction, SwitchAction]